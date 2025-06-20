from behave import given, when, then, step
import grpc
import os

# Imports directos de gRPC stubs
from app import mood_predictor_pb2_grpc
from app import mood_predictor_pb2


@given("el servidor MoodPredictor está en ejecución")
def step_impl_server_running(context):
    context.server_address = os.getenv("GRPC_SERVER_ADDRESS", "localhost:50051")
    print(f"Asumiendo que el servidor gRPC está en {context.server_address}")
    try:
        with grpc.insecure_channel(context.server_address) as channel:
            grpc.channel_ready_future(channel).result(timeout=1)
        print("Conexión de prueba al servidor exitosa.")
    except grpc.FutureTimeoutError:
        print(
            "ADVERTENCIA: No se pudo conectar al servidor gRPC en el health check inicial."
        )
        # context.abort("El servidor gRPC no está disponible.")


@when(
    "envío una solicitud para predecir el mood del usuario con las siguientes canciones:"
)
def step_impl_predict_with_songs(context):
    context.feature_song_features = []
    for row in context.table:
        sf = mood_predictor_pb2.SongFeatures(
            song_id=row["song_id"],
            tempo=float(row["tempo"]),
            energy=float(row["energy"]),
            valence=float(row["valence"]),
            danceability=float(row["danceability"]),
        )
        context.feature_song_features.append(sf)

    try:
        with grpc.insecure_channel(context.server_address) as channel:
            stub = mood_predictor_pb2_grpc.MoodPredictorServiceStub(channel)
            request = mood_predictor_pb2.PredictUserMoodRequest(
                song_features=context.feature_song_features
            )
            context.response = stub.PredictUserMood(request, timeout=10)
            context.grpc_error = None
    except grpc.RpcError as e:
        context.response = None
        context.grpc_error = e
        print(f"Error gRPC capturado: Code={e.code()} Details='{e.details()}'")
    except RuntimeError as e:
        context.abort(
            f"Fallo crítico en el step debido a stubs no cargados o error de runtime: {e}"
        )


@when("envío una solicitud para predecir el mood del usuario sin ninguna canción")
def step_impl_predict_no_songs(context):
    context.feature_song_features = []
    try:
        with grpc.insecure_channel(context.server_address) as channel:
            stub = mood_predictor_pb2_grpc.MoodPredictorServiceStub(channel)
            request = mood_predictor_pb2.PredictUserMoodRequest(
                song_features=context.feature_song_features
            )
            context.response = stub.PredictUserMood(request, timeout=10)
            context.grpc_error = None
    except grpc.RpcError as e:
        context.response = None
        context.grpc_error = e
        print(
            f"Error gRPC capturado (esperado para lista vacía): Code={e.code()} Details='{e.details()}'"
        )
    except RuntimeError as e:
        context.abort(
            f"Fallo crítico en el step debido a stubs no cargados o error de runtime: {e}"
        )


@then(
    'la respuesta debería indicar que el mood global del usuario es "{expected_mood}"'
)
def step_impl_check_global_mood(context, expected_mood):
    assert (
        context.grpc_error is None
    ), f"Se esperaba una respuesta exitosa, pero se obtuvo un error gRPC: Code={context.grpc_error.code()} Details='{context.grpc_error.details()}'"
    assert context.response is not None, "No se recibió respuesta del servidor."
    assert (
        context.response.global_mood == expected_mood
    ), f"Mood global esperado '{expected_mood}', pero se obtuvo '{context.response.global_mood}'"


@then('debería recibir un error de "{expected_error_code_str}"')
def step_impl_check_grpc_error(context, expected_error_code_str):
    assert (
        context.grpc_error is not None
    ), "Se esperaba un error gRPC, pero no se recibió ninguno."

    try:
        expected_grpc_code = getattr(grpc.StatusCode, expected_error_code_str)
    except AttributeError:
        raise ValueError(
            f"Código de error gRPC no reconocido en grpc.StatusCode: {expected_error_code_str}"
        )

    assert (
        context.grpc_error.code() == expected_grpc_code
    ), f"Se esperaba el código de error gRPC {expected_grpc_code} ('{expected_error_code_str}'), pero se obtuvo {context.grpc_error.code()} ('{context.grpc_error.details()}')"
