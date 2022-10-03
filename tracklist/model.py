from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TrackEntry:
    artist: str = ''
    title: str = ''
    start_seconds: int = 0

@dataclass
class Tracklist:
    artist: Optional[str] = None
    title: Optional[str] = None
    file: Optional[str] = None
    format: Optional[str] = None
    duration_seconds: Optional[int] = None
    entries: list[TrackEntry] = field(default_factory=list)
