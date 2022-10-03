from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TrackEntry:
    artist: str = ''
    title: str = ''
    start_seconds: int = 0

@dataclass
class Tracklist:
    name: Optional[str] = None
    file: Optional[str] = None
    entries: list[TrackEntry] = field(default_factory=list)
