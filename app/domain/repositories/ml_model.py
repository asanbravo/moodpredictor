from abc import ABC, abstractmethod
from app.domain.value_objects.song_features import SongFeatures
from app.domain.value_objects.mood_prediction import MoodPrediction


class MLModel(ABC):
    @abstractmethod
    def predict(self, features: SongFeatures) -> MoodPrediction:
        """
        Realiza una predicción basada en las características de la canción.
        """
        pass

    @abstractmethod
    def load_model(self, model_path: str):
        """
        Carga el modelo de machine learning desde un archivo.
        """
        pass
