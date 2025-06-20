from abc import ABC, abstractmethod
from typing import List
from app.domain.value_objects.song_features import SongFeatures

# Import MoodPrediction para el tipo de retorno de la lista de moods individuales
from app.domain.value_objects.mood_prediction import MoodPrediction


class MoodPredictionRepository(ABC):
    @abstractmethod
    async def predict_individual_moods(
        self, features_list: List[SongFeatures]
    ) -> List[MoodPrediction]:
        """
        Predice el estado de ánimo individual para una lista de canciones.
        """
        pass
