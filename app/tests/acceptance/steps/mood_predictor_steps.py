from behave import given, when, then, step
import grpc
import os
from app import mood_predictor_pb2_grpc
from app import mood_predictor_pb2


@given("the MoodPredictor server is running")
def step_impl_server_running(context):
    context.server_address = os.getenv("GRPC_SERVER_ADDRESS", "localhost:50051")

    try:
        with grpc.insecure_channel(context.server_address) as channel:
            grpc.channel_ready_future(channel).result(timeout=5)
        print(
            f"DEBUG CI: Successfully connected to gRPC server at {context.server_address}"
        )
        context.server_running = True
    except grpc.FutureTimeoutError:
        print(
            f"DEBUG CI: Failed to connect to gRPC server at {context.server_address} within timeout."
        )
        context.server_running = False
    pass


@when("I send a list of songs for mood prediction")
def step_impl_predict_with_song_list(context):
    if not getattr(context, "server_running", False) and not os.getenv(
        "FORCE_GRPC_CALLS_FOR_DEBUG"
    ):
        context.response = None
        context.grpc_error = grpc.FutureTimeoutError(
            "Skipped gRPC call because server presumed not running from @given step."
        )
        return

    context.feature_song_features = []
    if hasattr(context, "table") and context.table:
        # print(f"DEBUG CI TABLE: Rows: {len(context.table.rows)}, Headings: {context.table.headings}")
        for row in context.table:
            sf = mood_predictor_pb2.SongFeatures(
                song_id=row["song_id"],
                tempo=float(row["tempo"]),
                energy=float(row["energy"]),
                valence=float(row["valence"]),
                danceability=float(row["danceability"]),
            )
            context.feature_song_features.append(sf)
    else:
        print(
            "DEBUG CI TABLE: No table found in context for step 'I send a list of songs for mood prediction'."
        )

    try:
        with grpc.insecure_channel(context.server_address) as channel:
            stub = mood_predictor_pb2_grpc.MoodPredictorServiceStub(channel)
            request = mood_predictor_pb2.PredictUserMoodRequest(
                song_features=context.feature_song_features
            )
            print(
                f"DEBUG CI: Sending PredictUserMoodRequest with {len(context.feature_song_features)} songs."
            )
            context.response = stub.PredictUserMood(request, timeout=10)
            context.grpc_error = None
    except grpc.RpcError as e:
        context.response = None
        context.grpc_error = e
        print(
            f"DEBUG CI: gRPC RpcError captured: Code={e.code()} Details='{e.details()}'"
        )
    except Exception as e_gen:
        context.response = None
        context.grpc_error = e_gen


@when("I send a request to predict the user's mood with no songs")
def step_impl_predict_no_songs(context):
    print(
        "DEBUG CI: When step 'I send a request to predict the user's mood with no songs' EXECUTED."
    )
    if not getattr(context, "server_running", False) and not os.getenv(
        "FORCE_GRPC_CALLS_FOR_DEBUG"
    ):
        context.response = None
        context.grpc_error = grpc.FutureTimeoutError(
            "Skipped gRPC call because server presumed not running from @given step."
        )
        return

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
            f"DEBUG CI: gRPC RpcError captured (expected for no songs): Code={e.code()} Details='{e.details()}'"
        )
    except Exception as e_gen:
        context.response = None
        context.grpc_error = e_gen


@then('the response should indicate the user\'s global mood is "{expected_mood}"')
def step_impl_check_global_mood(context, expected_mood):
    print(
        f"DEBUG CI: Then step 'the response should indicate the user's global mood is \"{expected_mood}\"' EXECUTED."
    )
    # Helper to get error details safely
    error_details = "N/A"
    if context.grpc_error:
        if isinstance(
            context.grpc_error, grpc.RpcError
        ):  # Check if it's a real RpcError
            error_details = f"Code={context.grpc_error.code()} Details='{context.grpc_error.details()}'"
        elif isinstance(
            context.grpc_error, grpc.FutureTimeoutError
        ):  # Handle the FutureTimeoutError we might set
            error_details = f"FutureTimeoutError: {str(context.grpc_error)}"
        else:  # Handle other generic exceptions
            error_details = str(context.grpc_error)

    assert (
        context.grpc_error is None
    ), f"Expected a successful response, but got an error: {error_details}"
    assert (
        context.response is not None
    ), "No response received from the server, and no gRPC error was explicitly caught."
    assert (
        context.response.global_mood == expected_mood
    ), f"Expected global mood '{expected_mood}', but got '{context.response.global_mood}'"


@then('I should receive an "{expected_error_code_str}" error')
def step_impl_check_grpc_error(context, expected_error_code_str):
    print(
        f"DEBUG CI: Then step 'I should receive an \"{expected_error_code_str}\" error' EXECUTED."
    )
    assert (
        context.grpc_error is not None
    ), f"Expected a gRPC error '{expected_error_code_str}', but no gRPC error was caught."

    if not isinstance(context.grpc_error, grpc.RpcError):
        # This will now correctly fail if we manually set a FutureTimeoutError or generic Exception
        # when an RpcError from the server was expected.
        assert (
            False
        ), f"A gRPC RpcError was expected, but got {type(context.grpc_error)}: {str(context.grpc_error)}"

    expected_grpc_code = getattr(grpc.StatusCode, expected_error_code_str, None)
    if expected_grpc_code is None:
        raise ValueError(
            f"Unrecognized gRPC error code string in Gherkin step: '{expected_error_code_str}'"
        )

    assert (
        context.grpc_error.code() == expected_grpc_code
    ), f"Expected gRPC error code {expected_grpc_code} ('{expected_error_code_str}'), but got {context.grpc_error.code()}. Details: '{context.grpc_error.details()}'"
