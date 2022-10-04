from dataclasses import replace
from tracklist.model import Tracklist

def merge(tracklists: list[Tracklist]) -> Tracklist:
    """
    Merges the given tracklists, i.e. overlays them.
    """

    result = replace(tracklists[0], entries=[]) if tracklists else Tracklist()

    for tracklist in tracklists:
        result.entries += [replace(entry) for entry in tracklist.entries]

    result.entries.sort(key=lambda entry: entry.start_seconds)

    return result
