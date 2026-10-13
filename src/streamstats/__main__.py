import argparse
import logging
import sys
from pathlib import Path

from .errors import StreamStatsError


def create_parsers_for_cli() -> argparse.ArgumentParser:
    """
    This function creates parsers for command line interface with argparse library
    Input: None
    Output: parser for command line interface
    """

    parser = argparse.ArgumentParser(
        prog="python -m streamstats", description="Stream Stats Error"
    )
    subparser = parser.add_subparsers(dest="command", required=True)

    parser_analyze = subparser.add_parser(
        "analyze",
        help="Analyze the data and write report",
        description="Read line by line file and make statistics",
    )
    parser_analyze.add_argument(
        "input_data_files", nargs="+", type=Path, help="Input data"
    )
    parser_analyze.add_argument(
        "--format",
        dest="format_input_data",
        type=str,
        required=True,
        help="Input data format",
    )
    parser_analyze.add_argument(
        "--output", dest="output_data_file", type=Path, default=None, help="Output data"
    )
    parser_analyze.add_argument(
        "--skip-invalid",
        dest="skip_invalid",
        action="store_true",
        help="Skip invalid lines instead of stopping",
    )

    return parser


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.WARNING, format="{levelname}: {message}", style="{"
    )


def main() -> int:
    configure_logging()
    args = create_parsers_for_cli().parse_args()
    print(args)

    try:
        # validate_data(args)
        # run_analyze(args)
        sys.exit(0)
    except StreamStatsError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
