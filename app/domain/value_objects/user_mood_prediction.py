from dataclasses import dataclass
from .mood import Mood  # Import the Mood enum


@dataclass(frozen=True)
class UserMoodPrediction:
    global_mood: Mood  # Use the Mood enum
