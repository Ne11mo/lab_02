import csv
import json
import logging
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path

from .errors import InvalidEventError, InvalidFormatError, StreamStatsError
from .models import (
    AVAILABLE_FIELDS,
    Event,
    ParserStatistics,
    check_and_create_event_parser,
)

logger = logging.getLogger(__name__)

choice_parser_function = Callable[
    [Iterable[Path], bool, ParserStatistics], Iterator[Event]
]
FORMAT_PARSERS: dict[str, choice_parser_function] = {}


def register_parser(
    name: str,
) -> Callable[[choice_parser_function], choice_parser_function]:
    def decorator(parser_function: choice_parser_function) -> choice_parser_function:
        FORMAT_PARSERS[name] = parser_function
        return parser_function

    return decorator


@register_parser("csv")
def start_csv_parser(
    input_data: Iterable[Path],
    is_skip_invalid: bool,
    parser_statistics: ParserStatistics,
) -> Iterator[Event]:
    """
    This function parses the input csv files
    :param input_data: Iterable[Path]
    :param is_skip_invalid: bool
    :param parser_statistics: ParserStatistics
    :return Iterator[Event]
    """

    for file_number, path in enumerate(input_data, start=1):
        with path.open(newline="", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file, strict=True)

            try:
                fieldnames = csv_reader.fieldnames
            except csv.Error as e:
                raise InvalidEventError(
                    f"Ошибка: в файле {file_number} в строке 1 неверный csv заголовок - {e}"
                )

            if fieldnames is None:  # нет заголовков
                continue

            list_of_empty_fields = []
            for field in AVAILABLE_FIELDS:
                if field not in fieldnames:
                    list_of_empty_fields.append(field)

            if len(list_of_empty_fields) != 0:
                raise InvalidEventError(
                    f"Ошибка: в файле {file_number} отсутствуют обязательные поля: {list_of_empty_fields}"
                )

            rows = iter(csv_reader)
            while True:
                try:
                    try:
                        row = next(rows)
                    except csv.Error as e:
                        raise InvalidEventError(
                            f"Ошибка: в файле {file_number} в строке {csv_reader.line_num} некорректный csv - {e}"
                        )
                    event = check_and_create_event_parser(
                        row, file_number, csv_reader.line_num
                    )
                except StopIteration:
                    break
                except StreamStatsError:
                    if is_skip_invalid:
                        logger.warning(
                            f" В файле {file_number} пропущена строка {csv_reader.line_num}"
                        )
                        parser_statistics.skipped_lines += 1
                        continue
                    else:
                        raise
                yield event


@register_parser("jsonl")
def start_jsonl_parser(
    input_data: Iterable[Path],
    is_skip_invalid: bool,
    parser_statistics: ParserStatistics,
) -> Iterator[Event]:
    """
    This function parses the input jsonl files
    :param input_data: Iterable[Path]
    :param is_skip_invalid: bool
    :param parser_statistics: ParserStatistics
    :return Iterator[Event]
    """
    for file_number, path in enumerate(input_data, start=1):
        with path.open(encoding="utf-8") as jsonl_file:
            for line_number, line in enumerate(jsonl_file, start=1):
                try:
                    try:
                        line = json.loads(line)
                    except json.JSONDecodeError:
                        raise InvalidEventError(
                            f"Ошибка: в файле {file_number} в строке {line_number} некорректный jsonl "
                        )

                    if not isinstance(line, dict):
                        raise InvalidEventError(
                            f"Ошибка: в файле {file_number} в строке {line_number} ожидался jsonl объект"
                        )

                    event = check_and_create_event_parser(
                        line, file_number, line_number
                    )
                except StreamStatsError:
                    if is_skip_invalid:
                        logger.warning(
                            f"В файле {file_number} пропущена строка {line_number}"
                        )
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
) -> Iterator[Event]:
    """
    This function detected which parser the program need to use
    :param input_data: Iterable[Path]
    :param format_of_input_data: str
    :param is_skip_invalid: bool
    :param parser_statistics: ParserStatistics
    :return Iterator[Event]
    """

    extension_input_files = format_of_input_data.strip().lower()
    parser_function = FORMAT_PARSERS.get(extension_input_files)

    if parser_function is None:
        raise InvalidFormatError(f"Неподдерживаемый формат: {format_of_input_data}")

    return parser_function(input_data, is_skip_invalid, parser_statistics)
