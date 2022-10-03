import math
import shutil
import subprocess

from dataclasses import replace
from pathlib import Path

from tracklist.model import Tracklist

def resolve_duration(tracklist: Tracklist, parent_dir: Path) -> Tracklist:
    """
    Fills out the duration using ffprobe if ffprobe is on PATH
    and the duration is left unspecified.
    """

    if tracklist.duration_seconds is not None or not tracklist.file or not shutil.which('ffprobe'):
        return tracklist

    raw_duration = subprocess.run(
        [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            tracklist.file,
        ],
        capture_output=True,
        encoding='utf8',
        cwd=parent_dir
    ).stdout

    duration_seconds = math.floor(float(raw_duration))

    return replace(tracklist, duration_seconds=duration_seconds)
