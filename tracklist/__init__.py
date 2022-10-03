import argparse
import sys

from contextlib import nullcontext
from pathlib import Path
from typing import Optional

from tracklist.format import Format
from tracklist.format.cuesheet import CuesheetFormat
from tracklist.format.tabular import TabularFormat
from tracklist.model import Tracklist
from tracklist.transform.cat import cat
from tracklist.transform.ffprobe import resolve_duration

_FORMATS: dict[str, Format] = {
    'cue': CuesheetFormat(),
    'csv': TabularFormat(),
}

_TRANSFORMS = {
    'cat': cat,
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
    parser = argparse.ArgumentParser(description='Tracklist processor')
    parser.add_argument('-o', '--output', type=Path, help='The output file.')
    parser.add_argument('-f', '--format', choices=sorted(_FORMATS.keys()), help='The output format. Defaults to the format determined by the extension of the --output files and, if none are specified, to cuesheets.')
    parser.add_argument('transform', choices=sorted(_TRANSFORMS.keys()), help='The transform to perform.')
    parser.add_argument('inputs', type=Path, nargs='+', help='The input files.')

    args = parser.parse_args()
    input_paths = args.inputs
    output_path = args.output

    inputs = _read_inputs(input_paths)
    transform = _TRANSFORMS[args.transform]
    output = transform(inputs)

    output_format = None

    if args.format:
        output_format = _FORMATS[args.format]
    elif output_path:
        output_format = _file_format(output_path)
    
    if not output_format:
        output_format = _FORMATS['cue']
    
    _write_output(output, output_format, output_path)

