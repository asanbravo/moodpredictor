from typing import List
from collections import Counter  # Para calcular la moda
from app.domain.repositories.mood_prediction_repository import MoodPredictionRepository
from app.domain.value_objects.song_features import SongFeatures
from app.domain.value_objects.user_mood_prediction import UserMoodPrediction
from app.domain.value_objects.mood_prediction import (
    MoodPrediction,
)  # Para el tipo de la lista de moods individuales
from app.domain.value_objects.mood import Mood  # Para el enum Mood


class MoodPredictionService:
    def __init__(self, repository: MoodPredictionRepository):
        self.repository = repository

    async def predict_user_mood(
        self, features_list: List[SongFeatures]
    ) -> UserMoodPrediction:
        if not features_list:
            return UserMoodPrediction(global_mood=Mood.UNDEFINED)

        # Obtener predicciones individuales del repositorio
        # Ahora se llama predict_individual_moods y devuelve List[MoodPrediction]
        individual_mood_objects: List[MoodPrediction] = (
            await self.repository.predict_individual_moods(features_list)
        )

        if not individual_mood_objects:
            return UserMoodPrediction(global_mood=Mood.UNDEFINED)

        # Extraer los Mood enums de los objetos MoodPrediction
        mood_enums: List[Mood] = [
            pred.mood for pred in individual_mood_objects if pred.mood != Mood.UNDEFINED
        ]

        if (
            not mood_enums
        ):  # Si todas las predicciones fueron UNDEFINED o la lista original estaba vacía
            return UserMoodPrediction(global_mood=Mood.UNDEFINED)

        # Calcular la moda (el mood más frecuente)
        mood_counts = Counter(mood_enums)
        most_common_moods = mood_counts.most_common()

        # most_common_moods es una lista de tuplas (mood_enum, count)
        # Ej: [(<Mood.HAPPY: 'Happy'>, 5), (<Mood.SAD: 'Sad'>, 2)]

        if not most_common_moods:  # Debería ser redundante si mood_enums no está vacío
            return UserMoodPrediction(global_mood=Mood.UNDEFINED)

        # Manejo de empates:
        # Si hay un solo mood más común, ese es el resultado.
        # Si hay múltiples moods con la misma frecuencia más alta,
        # por ahora, simplemente tomaremos el primero de la lista de los más comunes.
        # Una lógica más sofisticada podría ser implementada aquí si se desea (ej. "Mixed").
        global_mood_enum = most_common_moods[0][0]

        return UserMoodPrediction(global_mood=global_mood_enum)
