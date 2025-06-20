from enum import Enum


class Mood(Enum):
    HAPPY = "Happy"
    SAD = "Sad"
    ENERGETIC = "Energetic"
    RELAXED = "Relaxed"
    UNDEFINED = "Undefined"

    @classmethod
    def list_valid_moods(cls):
        return [m.value for m in cls if m != cls.UNDEFINED]

    @classmethod
    def from_string(cls, mood_string: str):
        for mood_member in cls:
            if mood_member.value.lower() == mood_string.lower():
                return mood_member
        return cls.UNDEFINED
