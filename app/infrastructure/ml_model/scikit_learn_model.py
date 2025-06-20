import pandas as pd
import joblib
import os
from typing import List, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from app.domain.repositories.ml_model import MLModel
from app.domain.value_objects.song_features import SongFeatures
from app.domain.value_objects.mood import Mood
from app.domain.value_objects.mood_prediction import MoodPrediction


class ScikitLearnMoodModel(MLModel):
    MODEL_FILENAME = "mood_model.joblib"
    DEFAULT_DATASET_PATH = "songs_dataset.csv"

    def __init__(
        self,
        model_path: Optional[str] = None,
        dataset_path_for_training: Optional[str] = None,
        force_retrain: bool = False,
    ):
        self.model_file_path = model_path if model_path else self.MODEL_FILENAME
        self.dataset_to_use_for_training = (
            dataset_path_for_training
            if dataset_path_for_training
            else self.DEFAULT_DATASET_PATH
        )
        self.model = None
        self.label_encoder = LabelEncoder()
        model_dir = os.path.dirname(self.model_file_path)
        if model_dir and not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)
        if os.path.exists(self.model_file_path) and not force_retrain:
            print(f"Cargando modelo existente desde {self.model_file_path}")
            self.load_model(self.model_file_path)
        else:
            print(
                f"No se encontró el modelo en {self.model_file_path} o se forzó el reentrenamiento."
            )
            if not os.path.exists(self.dataset_to_use_for_training):
                print(
                    f"ERROR: Dataset '{self.dataset_to_use_for_training}' no encontrado. No se puede entrenar el modelo."
                )
                self.model = None
            else:
                self._train_and_save_model(self.dataset_to_use_for_training)

    def load_model(self, model_path: str):
        self.model_file_path = model_path
        try:
            data = joblib.load(self.model_file_path)
            self.model = data["model"]
            self.label_encoder = data["label_encoder"]
            print(f"Modelo y LabelEncoder cargados desde {self.model_file_path}")
        except FileNotFoundError:
            print(f"ERROR: Archivo de modelo no encontrado en {self.model_file_path}")
            self.model = None
        except Exception as e:
            print(f"Ocurrió un error al cargar el modelo: {e}")
            self.model = None

    def _fit_label_encoder(self, y_data):
        self.label_encoder.fit(y_data)

    def _train_and_save_model(self, dataset_path: str):
        print(f"Entrenando modelo desde {dataset_path}...")
        try:
            df = pd.read_csv(dataset_path)
            if df.empty:
                print(f"Dataset en {dataset_path} está vacío.")
                self.model = None
                return
            features_cols = ["tempo", "energy", "valence", "danceability"]
            target_col = "mood"
            X = df[features_cols]
            y = df[target_col]
            self._fit_label_encoder(y)
            y_encoded = self.label_encoder.transform(y)
            trained_model = RandomForestClassifier(
                n_estimators=10, random_state=42, class_weight="balanced"
            )  # Reduced estimators
            trained_model.fit(X, y_encoded)
            self.model = trained_model
            if self.model and self.model_file_path:
                joblib.dump(
                    {"model": self.model, "label_encoder": self.label_encoder},
                    self.model_file_path,
                )
                print(f"Modelo y LabelEncoder guardados en {self.model_file_path}")
        except FileNotFoundError:
            print(f"ERROR: Archivo de dataset no encontrado en {dataset_path}.")
            self.model = None
        except Exception as e:
            print(f"Ocurrió un error durante el entrenamiento: {e}")
            self.model = None

    def _prepare_features_for_prediction(self, fl: List[SongFeatures]):
        return (
            pd.DataFrame(
                {
                    "tempo": [f.tempo for f in fl],
                    "energy": [f.energy for f in fl],
                    "valence": [f.valence for f in fl],
                    "danceability": [f.danceability for f in fl],
                }
            )
            if fl
            else None
        )

    def predict(self, sf: SongFeatures):
        return self.predict_batch([sf])[0]

    def predict_batch(self, sfl: List[SongFeatures]):
        if not self.model or not sfl:
            print("Modelo no cargado o lista feats vacía.")
            return [MoodPrediction(mood=Mood.UNDEFINED) for _ in sfl]
        dff = self._prepare_features_for_prediction(sfl)
        if dff is None or dff.empty:
            print("DataFrame feats vacío.")
            return [MoodPrediction(mood=Mood.UNDEFINED) for _ in sfl]
        try:
            order = ["tempo", "energy", "valence", "danceability"]
            dff = dff[order]
            pe = self.model.predict(dff)
            ps = self.label_encoder.inverse_transform(pe)
            return [MoodPrediction(mood=Mood.from_string(str(s))) for s in ps]
        except Exception as e:
            print(f"Error en predicción batch: {e}")
            return [MoodPrediction(mood=Mood.UNDEFINED) for _ in sfl]
