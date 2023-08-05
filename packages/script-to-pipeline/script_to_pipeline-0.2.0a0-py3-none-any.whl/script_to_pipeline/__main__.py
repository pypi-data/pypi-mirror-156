from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint
from subprocess import run

from ._internal import convert_to_specification, write_pipeline


def main() -> None:
    script, pipeline, update, image = parse_args()
    specification = convert_to_specification(script, image)
    if pipeline:
        write_pipeline(pipeline, specification)
        if update:
            run(["pachctl", "update", "pipeline", "-f", str(pipeline), "--reprocess"])
    else:
        pprint(specification, indent=2)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("script", type=Path, metavar="FILE")
    parser.add_argument("--pipeline", default=None, type=Path)
    parser.add_argument("--image", default=None, type=str)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    if not args.script.exists():
        raise FileNotFoundError(args.script)
    return args.script, args.pipeline, args.update, args.image


if __name__ == "__main__":
    main()
