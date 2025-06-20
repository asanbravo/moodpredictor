import unittest
from unittest.mock import Mock, AsyncMock  # AsyncMock para métodos async del repo
from typing import List, Optional

# Clases y Enums necesarios del proyecto
from app.domain.value_objects.song_features import SongFeatures
from app.domain.value_objects.mood import Mood
from app.domain.value_objects.mood_prediction import MoodPrediction
from app.domain.value_objects.user_mood_prediction import UserMoodPrediction
from app.domain.repositories.mood_prediction_repository import MoodPredictionRepository
from app.application.services.mood_prediction_service import MoodPredictionService


# Un mock del repositorio para inyectar en el servicio
class MockMoodRepository(MoodPredictionRepository):
    def __init__(self):
        # Usamos AsyncMock para el método que será 'awaited'
        self.predict_individual_moods_mock = AsyncMock()

    async def predict_individual_moods(
        self, features_list: List[SongFeatures]
    ) -> List[MoodPrediction]:
        return await self.predict_individual_moods_mock(features_list)


class TestMoodPredictionService(
    unittest.IsolatedAsyncioTestCase
):  # Usar IsolatedAsyncioTestCase para tests async

    def setUp(self):
        self.mock_repository = MockMoodRepository()
        self.mood_service = MoodPredictionService(repository=self.mock_repository)

    async def test_predict_user_mood_basic_case_happy_mode(self):
        # Configurar el mock del repositorio para devolver moods individuales específicos
        mock_song_features = [
            SongFeatures(tempo=120, energy=0.8, valence=0.8, danceability=0.7)
        ]  # Contenido no importa mucho aquí

        individual_predictions = [
            MoodPrediction(mood=Mood.HAPPY),
            MoodPrediction(mood=Mood.HAPPY),
            MoodPrediction(mood=Mood.SAD),
        ]
        self.mock_repository.predict_individual_moods_mock.return_value = (
            individual_predictions
        )

        # Llamar al método del servicio
        result: UserMoodPrediction = await self.mood_service.predict_user_mood(
            mock_song_features
        )

        # Verificar que el mood global es el esperado (la moda)
        self.assertEqual(result.global_mood, Mood.HAPPY)
        self.mock_repository.predict_individual_moods_mock.assert_called_once_with(
            mock_song_features
        )

    async def test_predict_user_mood_empty_features_list(self):
        result: UserMoodPrediction = await self.mood_service.predict_user_mood([])
        self.assertEqual(result.global_mood, Mood.UNDEFINED)
        # El repositorio no debería ser llamado si la lista de features está vacía
        self.mock_repository.predict_individual_moods_mock.assert_not_called()

    async def test_predict_user_mood_all_individual_moods_undefined(self):
        mock_song_features = [
            SongFeatures(tempo=120, energy=0.8, valence=0.8, danceability=0.7)
        ]
        individual_predictions = [
            MoodPrediction(mood=Mood.UNDEFINED),
            MoodPrediction(mood=Mood.UNDEFINED),
        ]
        self.mock_repository.predict_individual_moods_mock.return_value = (
            individual_predictions
        )

        result: UserMoodPrediction = await self.mood_service.predict_user_mood(
            mock_song_features
        )
        self.assertEqual(result.global_mood, Mood.UNDEFINED)

    async def test_predict_user_mood_tie_case_clear_winner_after_tie(self):
        # Caso donde hay un claro ganador despues de un empate inicial entre otros moods
        mock_song_features = [
            SongFeatures(tempo=120, energy=0.8, valence=0.8, danceability=0.7)
        ]
        individual_predictions_clear_winner = [
            MoodPrediction(mood=Mood.HAPPY),  # 1
            MoodPrediction(mood=Mood.SAD),  # 1
            MoodPrediction(mood=Mood.HAPPY),  # 2
            MoodPrediction(mood=Mood.SAD),  # 2
            MoodPrediction(mood=Mood.HAPPY),  # 3 -> Happy es el ganador
        ]
        self.mock_repository.predict_individual_moods_mock.return_value = (
            individual_predictions_clear_winner
        )
        result: UserMoodPrediction = await self.mood_service.predict_user_mood(
            mock_song_features
        )
        self.assertEqual(result.global_mood, Mood.HAPPY)

    async def test_predict_user_mood_tie_favoring_first_encountered_by_counter(self):
        # Este test es para el caso de un empate real.
        # Counter.most_common() devuelve los elementos empatados en el orden en que se encontraron
        # por primera vez si sus cuentas finales son iguales.
        mock_song_features = [
            SongFeatures(tempo=120, energy=0.8, valence=0.8, danceability=0.7)
        ]
        # Aseguramos el orden de entrada para predecir el comportamiento de Counter
        individual_predictions = [
            MoodPrediction(
                mood=Mood.RELAXED
            ),  # RELAXED es el primero en alcanzar la cuenta de 2
            MoodPrediction(mood=Mood.ENERGETIC),
            MoodPrediction(mood=Mood.RELAXED),
            MoodPrediction(mood=Mood.ENERGETIC),
        ]  # Counts: Relaxed:2, Energetic:2.
        # Se espera que Relaxed sea el resultado.
        self.mock_repository.predict_individual_moods_mock.return_value = (
            individual_predictions
        )
        result: UserMoodPrediction = await self.mood_service.predict_user_mood(
            mock_song_features
        )
        self.assertEqual(result.global_mood, Mood.RELAXED)

    async def test_predict_user_mood_ignore_undefined_in_mode_calculation(self):
        mock_song_features = [
            SongFeatures(tempo=120, energy=0.8, valence=0.8, danceability=0.7)
        ]
        individual_predictions = [
            MoodPrediction(mood=Mood.SAD),
            MoodPrediction(mood=Mood.UNDEFINED),
            MoodPrediction(mood=Mood.SAD),
            MoodPrediction(mood=Mood.UNDEFINED),
            MoodPrediction(mood=Mood.HAPPY),
        ]  # Counts (sin UNDEFINED): Sad:2, Happy:1. Moda = Sad.
        self.mock_repository.predict_individual_moods_mock.return_value = (
            individual_predictions
        )
        result: UserMoodPrediction = await self.mood_service.predict_user_mood(
            mock_song_features
        )
        self.assertEqual(result.global_mood, Mood.SAD)

    async def test_predict_user_mood_single_valid_mood(self):
        mock_song_features = [
            SongFeatures(tempo=120, energy=0.8, valence=0.8, danceability=0.7)
        ]
        individual_predictions = [MoodPrediction(mood=Mood.ENERGETIC)]
        self.mock_repository.predict_individual_moods_mock.return_value = (
            individual_predictions
        )
        result: UserMoodPrediction = await self.mood_service.predict_user_mood(
            mock_song_features
        )
        self.assertEqual(result.global_mood, Mood.ENERGETIC)

    async def test_predict_user_mood_no_valid_individual_moods_from_repo_empty_list(
        self,
    ):
        mock_song_features = [
            SongFeatures(tempo=120, energy=0.8, valence=0.8, danceability=0.7)
        ]
        # El repositorio devuelve una lista vacía de predicciones
        self.mock_repository.predict_individual_moods_mock.return_value = []

        result: UserMoodPrediction = await self.mood_service.predict_user_mood(
            mock_song_features
        )
        self.assertEqual(result.global_mood, Mood.UNDEFINED)


if __name__ == "__main__":
    unittest.main()
