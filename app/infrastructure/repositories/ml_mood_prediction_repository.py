from typing import List
from app.domain.repositories.mood_prediction_repository import MoodPredictionRepository
from app.domain.repositories.ml_model import (
    MLModel,
)  # Asumiendo que MLModel es la interfaz para SklearnMoodModel
from app.domain.value_objects.song_features import SongFeatures
from app.domain.value_objects.mood_prediction import MoodPrediction
from app.domain.value_objects.mood import (
    Mood,
)  # Necesario si se maneja un caso UNDEFINED aquí


class MLMoodPredictionRepository(MoodPredictionRepository):
    def __init__(self, model: MLModel):
        self.model = model

    async def predict_individual_moods(
        self, features_list: List[SongFeatures]
    ) -> List[MoodPrediction]:
        if not features_list:
            return []  # Devuelve lista vacía si no hay características

        # SklearnMoodModel.predict_batch espera List[SongFeatures] y devuelve List[MoodPrediction]
        # donde MoodPrediction contiene un miembro Mood enum.
        individual_mood_predictions: List[MoodPrediction] = self.model.predict_batch(
            features_list
        )

        return individual_mood_predictions
