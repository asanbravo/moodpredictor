import asyncio
import grpc
from app import mood_predictor_pb2
from app import mood_predictor_pb2_grpc
from typing import List
from app.application.services.mood_prediction_service import MoodPredictionService
from app.domain.value_objects.song_features import SongFeatures as DomainSongFeatures
from app.domain.value_objects.user_mood_prediction import (
    UserMoodPrediction as DomainUserMoodPrediction,
)
from app.domain.value_objects.mood import Mood
from app.infrastructure.ml_model.scikit_learn_model import ScikitLearnMoodModel
from app.infrastructure.repositories.ml_mood_prediction_repository import (
    MLMoodPredictionRepository,
)


class MoodPredictorServiceImpl(mood_predictor_pb2_grpc.MoodPredictorServiceServicer):
    def __init__(self, prediction_service: MoodPredictionService):
        self.prediction_service = prediction_service

    async def PredictUserMood(
        self,
        request: mood_predictor_pb2.PredictUserMoodRequest,
        context: grpc.aio.ServicerContext,
    ) -> mood_predictor_pb2.PredictUserMoodResponse:
        if not request.song_features:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "La lista de características de canciones (song_features) no puede estar vacía.",
            )
            # abort() levanta una excepción, por lo que no se necesita un return aquí.

        domain_features_list: List[DomainSongFeatures] = []
        for req_features in request.song_features:
            df = DomainSongFeatures(
                song_id=req_features.song_id if req_features.song_id else None,
                tempo=req_features.tempo,
                energy=req_features.energy,
                valence=req_features.valence,
                danceability=req_features.danceability,
            )
            domain_features_list.append(df)

        domain_user_mood_prediction: DomainUserMoodPrediction = (
            await self.prediction_service.predict_user_mood(domain_features_list)
        )

        if not isinstance(domain_user_mood_prediction.global_mood, Mood):
            print(
                f"Error: global_mood no es una instancia de Mood enum: {type(domain_user_mood_prediction.global_mood)}"
            )
            await context.abort(
                grpc.StatusCode.INTERNAL,
                "Error interno al procesar la predicción del mood.",
            )

        return mood_predictor_pb2.PredictUserMoodResponse(
            global_mood=domain_user_mood_prediction.global_mood.value
        )


async def serve():
    server = grpc.aio.server()

    model_path = "mood_model.joblib"
    dataset_for_training = "songs_dataset.csv"

    mood_model = ScikitLearnMoodModel(
        model_path=model_path, dataset_path_for_training=dataset_for_training
    )

    if mood_model.model is None:
        print(
            "ADVERTENCIA CRÍTICA: El modelo de ML no pudo ser cargado ni entrenado. Las predicciones pueden no ser precisas o devolver UNDEFINED."
        )

    repository = MLMoodPredictionRepository(mood_model)
    prediction_service = MoodPredictionService(repository)

    mood_predictor_pb2_grpc.add_MoodPredictorServiceServicer_to_server(
        MoodPredictorServiceImpl(prediction_service), server
    )

    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    print(f"Servidor gRPC iniciando en {listen_addr}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
