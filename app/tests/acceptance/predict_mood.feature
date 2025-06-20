# language: en
Feature: User Mood Prediction
  As a client of the MoodPredictor API,
  I want to get a global user mood prediction
  based on the musical features of several of their songs.

  Scenario: Global mood prediction based on the mode of individual moods
    Given the MoodPredictor server is running
When I send a list of songs for mood prediction
      | song_id | tempo | energy | valence | danceability | expected_individual_mood |
      | happy_1 | 120.0 | 0.8   | 0.9     | 0.7          | Happy                    |
      | happy_2 | 130.0 | 0.85  | 0.85    | 0.75         | Happy                    |
      | sad_1   | 80.0  | 0.3   | 0.1     | 0.4          | Sad                      |
    Then the response should indicate the user's global mood is "Happy"

  Scenario: Global mood prediction with different individual moods
    Given the MoodPredictor server is running
When I send a list of songs for mood prediction
      | song_id | tempo | energy | valence | danceability | expected_individual_mood |
      | energetic_1 | 140.0 | 0.9  | 0.7  | 0.8  | Energetic                |
      | relaxed_1   | 90.0  | 0.4  | 0.6  | 0.5  | Relaxed                  |
      | energetic_2 | 145.0 | 0.88 | 0.6  | 0.7  | Energetic                |
    Then the response should indicate the user's global mood is "Energetic"

  Scenario: Global mood prediction with a single song
    Given the MoodPredictor server is running
When I send a list of songs for mood prediction
      | song_id         | tempo | energy | valence | danceability | expected_individual_mood |
      | sad_track_alone | 75.0  | 0.25   | 0.15    | 0.33         | Sad                      |
    Then the response should indicate the user's global mood is "Sad"

  Scenario: Global mood prediction with empty song input
    Given the MoodPredictor server is running
    When I send a request to predict the user's mood with no songs
    Then I should receive an "INVALID_ARGUMENT" error
