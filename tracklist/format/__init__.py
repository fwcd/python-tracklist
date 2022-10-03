from typing import Protocol

from tracklist.model import Tracklist

class Format(Protocol):
    """A tracklist format."""

    def parse(self, raw: str) -> Tracklist:
        """Converts the given tracklist from the format."""
        raise NotImplementedError(f'Cannot parse {type(self).__name__}')

    def format(self, tracklist: Tracklist) -> str:
        """Converts the given tracklist to the format."""
        raise NotImplementedError(f'Cannot format {type(self).__name__}')
