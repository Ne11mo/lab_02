import csv
import json
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Generator, Iterator

from src.streamstats.models import Event

from .errors import InvalidEventError, InvalidFormatError, StreamStatsError
from .models import AVAILABLE_FIELDS, ParserStatistics, check_and_create_event_parser

logger = logging.getLogger(__name__)


def start_csv_parser(
    input_data: Iterable[Path],
    is_skip_invalid: bool,
    parser_statistics: ParserStatistics,
) -> Iterator[Event] | None:
    """
    This function parses the input csv files
    :param parser_statistics:
    :param input_data
    :param is_skip_invalid
    :return Generator[Event, Any, None] | None
    """

    for file_number, path in enumerate(input_data, start=1):
        with path.open(newline="", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file, strict=True)

            try:
                fieldnames = csv_reader.fieldnames
            except csv.Error as e:
                raise InvalidEventError(
                    f"В файле №{file_number} ({path}) в строке 1 неверный csv заголовок: {e}"
                )

            if fieldnames is None:  # нет заголовков
                continue

            list_of_empty_fields = []
            for field in AVAILABLE_FIELDS:
                if field not in fieldnames:
                    list_of_empty_fields.append(field)

            if len(list_of_empty_fields) != 0:
                raise InvalidEventError(
                    f"В файле №{file_number} ({path}) отсутствуют обязательные поля: {list_of_empty_fields}"
                )

            for row in csv_reader:
                try:
                    event = check_and_create_event_parser(row)
                except StreamStatsError:
                    if is_skip_invalid:
                        logger.warning("Пропущена строка: %d", csv_reader.line_num)
                        parser_statistics.skipped_lines += 1
                        continue
                    else:
                        raise
                yield event


def start_jsonl_parser(
    input_data: Iterable[Path],
    is_skip_invalid: bool,
    parser_statistics: ParserStatistics,
) -> Iterator[Event] | None:
    for path in input_data:
        with path.open(encoding="utf-8") as jsonl_file:
            for line_number, line in enumerate(jsonl_file, start=1):
                try:
                    try:
                        line = json.loads(line)
                    except json.JSONDecodeError:
                        raise InvalidEventError("Некорректный jsonl ")

                    if not isinstance(line, dict):
                        raise InvalidEventError("Ожидался jsonl объект")

                    event = check_and_create_event_parser(line)
                except StreamStatsError:
                    if is_skip_invalid:
                        logger.warning("Пропущена строка: %d", line_number)
                        parser_statistics.skipped_lines += 1
                        continue
                    else:
                        raise
                yield event


def start_parser_of_input_data(
    input_data: Iterable[Path],
    format_of_input_data: str,
    is_skip_invalid: bool,
    parser_statistics: ParserStatistics,
) -> Generator[Event, Any, None] | None:
    """
    This function detected which parser the program need to use
    :param parser_statistics:
    :param input_data:
    :param format_of_input_data:
    :param is_skip_invalid:
    :return Generator[Event, Any, None] | None
    """

    if format_of_input_data == "csv":
        return start_csv_parser(input_data, is_skip_invalid, parser_statistics)
    if format_of_input_data == "jsonl":
        return start_jsonl_parser(input_data, is_skip_invalid, parser_statistics)

    raise InvalidFormatError(f"Неподдерживаемый формат: {format_of_input_data}")
