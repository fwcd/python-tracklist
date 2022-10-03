import re

from tracklist.format import Format
from tracklist.model import TrackEntry, Tracklist
from tracklist.utils import quote

def _parse_time(raw: str) -> int:
    minutes, seconds = map(int, raw.split(':')[:2])
    return 60 * minutes + seconds

def _format_time(total_seconds: int) -> str:
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f'{minutes:02}:{seconds:02}:00'

_FILE_PATTERN = re.compile(r'^FILE\s+"(?P<file>[^"]*)"\s+(?P<format>\w+)')
_TRACK_PATTERN = re.compile(r'^TRACK\s+(?P<index>\d+)\s+(?P<type>\S+)')
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
                if match := _FILE_PATTERN.search(line):
                    tracklist.file = match['file']
                    tracklist.format = match['format']
                elif match := _TRACK_PATTERN.search(line):
                    if match['type'] == 'AUDIO':
                        if entry:
                            tracklist.entries.append(entry)
                        entry = TrackEntry()
                elif entry:
                    if match := _TITLE_PATTERN.search(line):
                        entry.title = match['title']
                    elif match := _PERFORMER_PATTERN.search(line):
                        entry.artist = match['performer']
                    elif match := _INDEX_PATTERN.search(line):
                        entry.start_seconds = _parse_time(match['time'])
                elif match := _TITLE_PATTERN.search(line):
                    tracklist.title = match['title']
                elif match := _PERFORMER_PATTERN.search(line):
                    tracklist.artist = match['performer']

        if entry:
            tracklist.entries.append(entry)

        return tracklist
    
    def format(self, tracklist: Tracklist) -> str:
        return '\n'.join(' '.join([key, *args]) for key, args in [
            ('TITLE', [quote(tracklist.title)] if tracklist.title else None),
            ('PERFORMER', [quote(tracklist.artist)] if tracklist.artist else None),
            ('FILE', [quote(tracklist.file or ''), tracklist.format or 'WAVE']),
            *[row for i, entry in enumerate(tracklist.entries) for row in [
                ('  TRACK', [f'{i + 1:02}', 'AUDIO']),
                ('    TITLE', [quote(entry.title)]),
                ('    PERFORMER', [quote(entry.artist)]),
                ('    INDEX', ['01', _format_time(entry.start_seconds)]),
            ]]
        ] if args)
