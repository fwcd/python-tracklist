from tracklist.format import Format
from tracklist.model import TrackEntry, Tracklist

class TabularFormat(Format):
    """A CSV-like format with a custom separator."""

    def __init__(self, separator: str=','):
        self.separator = separator

    def parse(self, raw: str) -> Tracklist:
        entries = []

        for line in raw.splitlines():
            split = line.strip().split(self.separator)
            if len(split) >= 3:
                entries.append(TrackEntry(
                    artist=split[0],
                    title=split[1],
                    start_seconds=int(split[2])
                ))
        
        return Tracklist(entries=entries)
    
    def format(self, tracklist: Tracklist) -> str:
        def sanitize(s: str) -> str:
            return s.replace(self.separator, ' ')

        lines = []

        for track in tracklist.entries:
            line = self.separator.join([
                sanitize(track.artist),
                sanitize(track.title),
                str(track.start_seconds)
            ])
            lines.append(line)
        
        return '\n'.join(lines)
