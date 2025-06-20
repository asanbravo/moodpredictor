from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SongFeatures:
    tempo: float
    energy: float
    valence: float
    danceability: float
    song_id: Optional[str] = None
