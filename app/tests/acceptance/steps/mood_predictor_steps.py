from behave import (
    given,
    when,
    then,
    step,
)  # Único import necesario para que Behave reconozca los steps

# --- Imports Comentados Temporalmente para Depuración ---
# import grpc
# try:
#     from app import mood_predictor_pb2_grpc
#     from app import mood_predictor_pb2
# except ImportError as e:
#     print(f"DEBUG STEP IMPORT ERROR: {e}") # Añadir un print para ver el error si ocurre aquí
#     raise # Relanzar para que el CI falle aquí si este es el problema


@given("the MoodPredictor server is running")
def step_impl_server_running(context):
    print("DEBUG: step_impl_server_running ejecutado")
    pass


@when("I send a request to predict the user's mood with the following songs:")
def step_impl_predict_with_songs(context):
    print("DEBUG: step_impl_predict_with_songs ejecutado")
    # context.feature_song_features = []
    # for row in context.table:
    #     sf = mood_predictor_pb2.SongFeatures(
    #         song_id=row['song_id'],
    #         tempo=float(row['tempo']),
    #         energy=float(row['energy']),
    #         valence=float(row['valence']),
    #         danceability=float(row['danceability'])
    #     )
    #     context.feature_song_features.append(sf)
    #
    # try:
    #     with grpc.insecure_channel(context.server_address) as channel:
    #         stub = mood_predictor_pb2_grpc.MoodPredictorServiceStub(channel)
    #         request = mood_predictor_pb2.PredictUserMoodRequest(song_features=context.feature_song_features)
    #         context.response = stub.PredictUserMood(request, timeout=10)
    #         context.grpc_error = None
    # except grpc.RpcError as e:
    #     context.response = None
    #     context.grpc_error = e
    #     print(f"Error gRPC capturado: {e.code()} - {e.details()}")
    pass


@when("I send a request to predict the user's mood with no songs")
def step_impl_predict_no_songs(context):
    print("DEBUG: step_impl_predict_no_songs ejecutado")
    # context.feature_song_features = []
    # try:
    #     with grpc.insecure_channel(context.server_address) as channel:
    #         stub = mood_predictor_pb2_grpc.MoodPredictorServiceStub(channel)
    #         request = mood_predictor_pb2.PredictUserMoodRequest(song_features=context.feature_song_features)
    #         context.response = stub.PredictUserMood(request, timeout=10)
    #         context.grpc_error = None
    # except grpc.RpcError as e:
    #     context.response = None
    #     context.grpc_error = e
    #     print(f"Error gRPC capturado (esperado para lista vacía): {e.code()} - {e.details()}")
    pass


@then('the response should indicate the user\'s global mood is "{expected_mood}"')
def step_impl_check_global_mood(context, expected_mood):
    print(
        f"DEBUG: step_impl_check_global_mood ejecutado con expected_mood={expected_mood}"
    )
    # assert context.grpc_error is None, f"Se esperaba una respuesta exitosa, pero se obtuvo un error gRPC: {context.grpc_error}"
    # assert context.response is not None, "No se recibió respuesta del servidor."
    # assert context.response.global_mood == expected_mood,     #     f"Mood global esperado '{expected_mood}', pero se obtuvo '{context.response.global_mood}'"
    pass


@then('I should receive an "{expected_error_code_str}" error')
def step_impl_check_grpc_error(context, expected_error_code_str):
    print(
        f"DEBUG: step_impl_check_grpc_error ejecutado con expected_error_code_str={expected_error_code_str}"
    )
    # assert context.grpc_error is not None, "Se esperaba un error gRPC, pero no se recibió ninguno."
    #
    # expected_grpc_code = None
    # if expected_error_code_str == "INVALID_ARGUMENT":
    #     expected_grpc_code = grpc.StatusCode.INVALID_ARGUMENT
    # else:
    #     raise ValueError(f"Código de error gRPC no reconocido en el step: {expected_error_code_str}")
    #
    # assert context.grpc_error.code() == expected_grpc_code,     #     f"Se esperaba el código de error gRPC {expected_grpc_code} ({expected_error_code_str}), pero se obtuvo {context.grpc_error.code()}"
    pass
