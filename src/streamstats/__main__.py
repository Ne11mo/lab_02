import argparse
import logging
import sys
from pathlib import Path

from .analysis import start_analyze
from .errors import StreamStatsError
from .models import ParserStatistics, check_input_paths_of_files
from .parsers import start_parser_of_input_data
from .report import write_report


def create_parsers_for_cli() -> argparse.ArgumentParser:
    """
    This function creates parsers for command line interface with argparse library
    input: None
    :return parser for command line interface
    """

    parser = argparse.ArgumentParser(
        prog="python -m streamstats", description="Stream Stats csv/jsonl reader"
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
    """
    Configure root logger
    input: None
    :return None
    """
    logging.basicConfig(level=logging.WARNING)


def main() -> None:
    """
    Main function
    input: None
    :return None
    """

    configure_logging()
    args = create_parsers_for_cli().parse_args()

    try:
        check_input_paths_of_files(args.input_data_files)

        parser_statistics = ParserStatistics()
        events = start_parser_of_input_data(
            args.input_data_files,
            args.format_input_data,
            args.skip_invalid,
            parser_statistics,
        )

        report = start_analyze(events, parser_statistics)
        write_report(report, args.output_data_file)
        sys.exit(0)
    except StreamStatsError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"Ошибка ввода-вывода: {e}", file=sys.stderr)
        sys.exit(2)
    except UnicodeDecodeError as e:
        print(f"Файл не в кодировке UTF-8: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
