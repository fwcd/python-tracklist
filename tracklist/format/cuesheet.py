import re

from tracklist.format import Format
from tracklist.model import TrackEntry, Tracklist

def _parse_time(raw: str) -> int:
    minutes, seconds = map(int, raw.split(':')[:2])
    return 60 * minutes + seconds

_FILE_PATTERN = re.compile(r'^FILE\s+"(?P<file>[^"]*)"\s+(\w+)')
_TRACK_PATTERN = re.compile(r'^TRACK\s+(?P<index>\d+)')
_TITLE_PATTERN = re.compile(r'^TITLE\s+"(?P<title>[^"]*)"')
_PERFORMER_PATTERN = re.compile(r'^PERFORMER\s+"(?P<performer>[^"]*)"')
_INDEX_PATTERN = re.compile(r'^INDEX\s+(?P<index>\d+)\s+(?P<time>[\d:]+)')

class CuesheetFormat(Format):
    """The classic cue sheet format, as known from CDs and e.g. Mixxx's recordings."""

    def parse(self, raw: str) -> Tracklist:
        tracklist = Tracklist()
        entry = None

        for line in raw.splitlines():
            line = line.strip()
            if line:
                if entry:
                    if match := _TITLE_PATTERN.search(line):
                        entry.title = match['title']
                    elif match := _PERFORMER_PATTERN.search(line):
                        entry.artist = match['performer']
                    elif match := _INDEX_PATTERN.search(line):
                        entry.start_seconds = _parse_time(match['time'])
                else:
                    if match := _FILE_PATTERN.search(line):
                        tracklist.file = match[1]
                    elif match := _TRACK_PATTERN.search(line):
                        if entry:
                            tracklist.entries.append(entry)
                        entry = TrackEntry()
                    elif match := _TITLE_PATTERN.search(line):
                        tracklist.title = match['title']
                    elif match := _PERFORMER_PATTERN.search(line):
                        tracklist.artist = match['performer']

        if entry:
            tracklist.entries.append(entry)

        return tracklist
    
    def format(self, tracklist: Tracklist) -> str:
        raise NotImplementedError('TODO')
