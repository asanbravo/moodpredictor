Feature: Predicción del estado de ánimo del usuario
  Como cliente de la API MoodPredictor,
  quiero obtener una predicción del estado de ánimo global de un usuario
  basada en las características de varias de sus canciones.

  Scenario: Predicción de mood global basada en la moda de moods individuales
    Given el servidor MoodPredictor está en ejecución
    When envío una solicitud para predecir el mood del usuario con las siguientes canciones:
      | song_id | tempo | energy | valence | danceability | expected_individual_mood |
      | happy_1 | 120.0 | 0.8   | 0.9     | 0.7          | Happy                    |
      | happy_2 | 130.0 | 0.85  | 0.85    | 0.75         | Happy                    |
      | sad_1   | 80.0  | 0.3   | 0.1     | 0.4          | Sad                      |
    Then la respuesta debería indicar que el mood global del usuario es "Happy"

  Scenario: Predicción de mood global con diferentes moods individuales
    Given el servidor MoodPredictor está en ejecución
    When envío una solicitud para predecir el mood del usuario con las siguientes canciones:
      | song_id | tempo | energy | valence | danceability | expected_individual_mood |
      | energetic_1 | 140.0 | 0.9  | 0.7  | 0.8  | Energetic                |
      | relaxed_1   | 90.0  | 0.4  | 0.6  | 0.5  | Relaxed                  |
      | energetic_2 | 145.0 | 0.88 | 0.6  | 0.7  | Energetic                |
    Then la respuesta debería indicar que el mood global del usuario es "Energetic"

  Scenario: Predicción de mood global con una sola canción
    Given el servidor MoodPredictor está en ejecución
    When envío una solicitud para predecir el mood del usuario con las siguientes canciones:
      | song_id | tempo | energy | valence | danceability | expected_individual_mood |
      | sad_track_alone | 75.0  | 0.25 | 0.15 | 0.33         | Sad                      |
    Then la respuesta debería indicar que el mood global del usuario es "Sad"

  Scenario: Predicción de mood global con entrada vacía de canciones
    Given el servidor MoodPredictor está en ejecución
    When envío una solicitud para predecir el mood del usuario sin ninguna canción
    Then debería recibir un error de "INVALID_ARGUMENT"
