from dataclasses import replace
from tracklist.model import Tracklist

def cat(tracklists: list[Tracklist]) -> Tracklist:
    """
    Concatenates the given tracklists.
    Requires every tracklist except for the last to have a specified duration.
    """

    result = replace(tracklists[0], entries=[]) if tracklists else Tracklist()
    start_seconds = 0

    for i, tracklist in enumerate(tracklists):
        result.entries += [replace(entry, start_seconds=start_seconds + entry.start_seconds) for entry in tracklist.entries]
        if i < len(tracklists) - 1:
            if tracklist.duration_seconds is None:
                raise ValueError('Tracklist duration must not be None to perform concatenation.')
            start_seconds += tracklist.duration_seconds

    return result
