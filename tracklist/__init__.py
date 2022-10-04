import argparse
import textwrap
import sys

from contextlib import nullcontext
from pathlib import Path
from typing import Optional

from tracklist.format import Format
from tracklist.format.cuesheet import CuesheetFormat
from tracklist.format.tabular import TabularFormat
from tracklist.model import Tracklist
from tracklist.aggregate.cat import cat
from tracklist.aggregate.merge import merge
from tracklist.resolve.ffprobe import resolve_duration

_FORMATS: dict[str, Format] = {
    'cue': CuesheetFormat(),
    'csv': TabularFormat(),
    'colons': TabularFormat(separator=' :: '),
}

_AGGREGATIONS = {
    'cat': cat,
    'merge': merge,
}

def _file_format(path: Path) -> Optional[Format]:
    return _FORMATS.get(path.suffix.split('.')[-1], None)

def _open(path: Path, mode: str):
    if str(path) == '-':
        if 'r' in mode:
            return nullcontext(sys.stdin)
        else:
            return nullcontext(sys.stdout)
    else:
        return open(path, mode)

def _read_inputs(paths: list[Path]) -> list[Tracklist]:
    inputs: list[Tracklist] = []

    for path in paths:
        format = _file_format(path)
        if format is None:
            print(f"Format of {path} was not recognized, the following are supported: {', '.join(sorted(_FORMATS.keys()))}")
            sys.exit(1)

        with _open(path, 'r') as f:
            tracklist = format.parse(f.read())
            tracklist = resolve_duration(tracklist, path.resolve().parent)
            inputs.append(tracklist)
    
    return inputs

def _write_output(tracklist: Tracklist, format: Format, path: Optional[Path]=None):
    with _open(path or Path('-'), 'w') as f:
        f.write(format.format(tracklist) + '\n')

def main():
    parser = argparse.ArgumentParser(
        description='Tracklist processor',
        epilog=textwrap.dedent('''
            examples:
              tracklist merge a.cue b.cue > out.cue # Overlay two cuesheets
              tracklist cat   a.cue b.cue > out.cue # Concatenate two cuesheets
              tracklist -f csv     cat in.cue       # Convert a cuesheet to CSV
              tracklist -o out.csv cat in.cue       # Convert a cuesheet to a CSV file
            '''
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('-o', '--output', type=Path, help='The output file.')
    parser.add_argument('-f', '--format', choices=sorted(_FORMATS.keys()), help='The output format. Defaults to the format determined by the extension of the --output files and, if none are specified, to cuesheets.')
    parser.add_argument('aggregation', choices=sorted(_AGGREGATIONS.keys()), help='The aggregation to perform.')
    parser.add_argument('inputs', type=Path, nargs='+', help='The input files.')

    args = parser.parse_args()
    input_paths = args.inputs
    output_path = args.output

    inputs = _read_inputs(input_paths)
    aggregation = _AGGREGATIONS[args.aggregation]
    output = aggregation(inputs)

    output_format = None

    if args.format:
        output_format = _FORMATS[args.format]
    elif output_path:
        output_format = _file_format(output_path)
    
    if not output_format:
        output_format = _FORMATS['cue']
    
    _write_output(output, output_format, output_path)

