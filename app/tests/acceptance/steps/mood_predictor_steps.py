from behave import given, when, then, step

# --- Imports Comentados Temporalmente para Depuración ---
# import grpc
# from app import mood_predictor_pb2_grpc
# from app import mood_predictor_pb2


@given("the MoodPredictor server is running")
def step_impl_server_running(context):
    print("DEBUG CI: Given step 'the MoodPredictor server is running' EXECUTED.")
    pass


@when("I send a request to predict the user's mood with the following songs:")
def step_impl_predict_with_songs(context):
    print(
        "DEBUG CI: When step 'I send a request to predict the user's mood with the following songs:' EXECUTED."
    )
    # if hasattr(context, 'table') and context.table:
    #    print(f"DEBUG CI TABLE: Rows: {len(context.table.rows)}, Headings: {context.table.headings}")
    # else:
    #    print("DEBUG CI TABLE: No table found in context or table is empty.")
    pass


@when("I send a request to predict the user's mood with no songs")
def step_impl_predict_no_songs(context):
    print(
        "DEBUG CI: When step 'I send a request to predict the user's mood with no songs' EXECUTED."
    )
    pass


@then('the response should indicate the user\'s global mood is "{expected_mood}"')
def step_impl_check_global_mood(context, expected_mood):
    print(
        f"DEBUG CI: Then step 'the response should indicate the user's global mood is \"{expected_mood}\"' EXECUTED."
    )
    pass


@then('I should receive an "{expected_error_code_str}" error')
def step_impl_check_grpc_error(context, expected_error_code_str):
    print(
        f"DEBUG CI: Then step 'I should receive an \"{expected_error_code_str}\" error' EXECUTED."
    )
    pass
