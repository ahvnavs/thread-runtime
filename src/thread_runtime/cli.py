"""THREAD Runtime command-line interface."""

import argparse
from importlib.metadata import version as get_version


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="thread",
        description="THREAD Runtime",
    )

    pkg_version = get_version("thread-runtime")

    parser.add_argument(
        "--version",
        action="version",
        version=f"THREAD Runtime {pkg_version}",
    )

    return parser


def main() -> int:
    parser = build_parser()
    parser.parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
