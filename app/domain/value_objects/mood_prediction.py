from dataclasses import dataclass
from app.domain.value_objects.mood import Mood


@dataclass(frozen=True)
class MoodPrediction:
    mood: Mood
