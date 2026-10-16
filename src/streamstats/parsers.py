import csv
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Generator

from src.streamstats.models import Event

from .errors import InvalidEventError, InvalidFormatError, StreamStatsError
from .models import check_and_create_event_parser

logger = logging.getLogger(__name__)


def start_csv_parser(
    input_data: Iterable[Path], is_skip_invalid: bool
) -> Generator[Event, Any, None] | None:
    file_number = 1
    for path in input_data:
        # добавить проверку на правильный путь файла и доступа
        with path.open(newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile, strict=True)

            try:
                fieldnames = csv_reader.fieldnames
            except csv.Error as e:
                raise InvalidEventError(
                    f"В файле №{file_number} ({path}) в строке 1 неверный csv заголовок: {e}"
                )

            if fieldnames is None:
                continue

            line_count = 1
            for row in csv_reader:
                try:
                    event = check_and_create_event_parser(row)
                except StreamStatsError:
                    if is_skip_invalid:
                        # лог выводит warning добавить
                        logger.warning("Пропущена строка: %d", csv_reader.line_num)
                        continue
                    else:
                        raise
                line_count += 1
                yield event

        file_number += 1


def start_json_parser(input_data: Iterable[Path], is_skip_invalid: bool) -> None:
    pass


def start_parser_of_input_data(
    input_data: Iterable[Path], format_of_input_data: str, is_skip_invalid: bool
) -> Generator[Event, Any, None] | None:
    if format_of_input_data == "csv":
        return start_csv_parser(input_data, is_skip_invalid)
    if format_of_input_data == "jsonl":
        return start_json_parser(input_data, is_skip_invalid)

    raise InvalidFormatError(f"Неподдерживаемый формат: {format_of_input_data}")
