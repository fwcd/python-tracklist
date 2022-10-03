from tracklist.format import Format
from tracklist.model import TrackEntry, Tracklist

def parse_quoted(raw: str) -> str:
    return raw.removeprefix('"').removesuffix('"')

def parse_time(raw: str) -> int:
    minutes, seconds = map(int, raw.split(':')[:2])
    return 60 * minutes + seconds

class CuesheetFormat(Format):
    """The classic cue sheet format, as known from CDs and e.g. Mixxx's recordings."""

    def parse(self, raw: str) -> Tracklist:
        entries = []
        entry = None

        for line in raw.splitlines():
            split = line.strip().split(' ', maxsplit=1)
            if split:
                if split[0] == 'TRACK':
                    if entry:
                        entries.append(entry)
                    entry = TrackEntry()
                elif entry:
                    if split[0] == 'TITLE':
                        entry.title = parse_quoted(split[1])
                    elif split[0] == 'PERFORMER':
                        entry.artist = parse_quoted(split[1])
                    elif split[0] == 'INDEX':
                        entry.start_seconds = parse_time(split[1].split(' ')[-1])

        if entry:
            entries.append(entry)

        return Tracklist(entries=entries)
    
    def format(self, tracklist: Tracklist) -> str:
        raise NotImplementedError('TODO')
