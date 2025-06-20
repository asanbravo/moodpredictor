from behave import given, when, then, step
import grpc
import os  # Para construir paths si es necesario

# Intentar importar los stubs gRPC desde la ubicación esperada
# Esto asume que 'behave' se ejecuta desde la raíz del proyecto, y PYTHONPATH incluye la raíz.
try:
    from app import mood_predictor_pb2_grpc
    from app import mood_predictor_pb2
except ImportError as e:
    print(
        f"ADVERTENCIA (Behave Steps): No se pudieron importar los stubs gRPC: {e}. Las pruebas de aceptación fallarán si se ejecutan."
    )

    # Definir placeholders para que el archivo de pasos al menos se cargue y no de error de sintaxis
    class _PlaceholderStub:
        @staticmethod
        def MoodPredictorServiceStub(channel):
            raise RuntimeError("Stubs gRPC no importados correctamente.")

    class _PlaceholderMessages:
        @staticmethod
        def SongFeatures(**kwargs):
            raise RuntimeError("Stubs gRPC no importados correctamente.")

        @staticmethod
        def PredictUserMoodRequest(song_features=None):
            raise RuntimeError("Stubs gRPC no importados correctamente.")

    mood_predictor_pb2_grpc = _PlaceholderStub()
    mood_predictor_pb2 = _PlaceholderMessages()


@given("el servidor MoodPredictor está en ejecución")
def step_impl_server_running(context):
    context.server_address = os.getenv("GRPC_SERVER_ADDRESS", "localhost:50051")
    print(f"Asumiendo que el servidor gRPC está en {context.server_address}")
    # Se podría añadir un intento de conexión simple aquí como un health check básico.
    try:
        with grpc.insecure_channel(context.server_address) as channel:
            grpc.channel_ready_future(channel).result(timeout=1)  # Timeout de 1 segundo
        print("Conexión de prueba al servidor exitosa.")
    except grpc.FutureTimeoutError:
        print(
            "ADVERTENCIA: No se pudo conectar al servidor gRPC en el health check inicial."
        )
        # Podríamos decidir abortar aquí con context.abort() si la conexión es vital para continuar.
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
    except RuntimeError as e:  # Captura el error de stubs no cargados
        context.abort(f"Fallo crítico en el step debido a stubs no cargados: {e}")


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
    except RuntimeError as e:  # Captura el error de stubs no cargados
        context.abort(f"Fallo crítico en el step debido a stubs no cargados: {e}")


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
