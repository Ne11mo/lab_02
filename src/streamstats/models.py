from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from .errors import CLIConfigurationError, InvalidEventError, InvalidTimeMarkerError

AVAILABLE_FIELDS = (
    "timestamp",
    "level",
    "source",
    "message",
)


class Level(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class Event:
    timestamp: datetime
    level: Level
    source: str
    message: str


@dataclass
class ParserStatistics:
    skipped_lines: int = 0


def check_input_paths_of_files(input_data_files: Iterable[Path]) -> None:
    for file_path in input_data_files:
        if not file_path.is_file():
            raise CLIConfigurationError(
                "Неправильный путь к файлу или несуществующий файл"
            )


def check_and_create_timestamp(
    time: str, file_number: int, line_number: int
) -> datetime:
    try:
        timestamp = datetime.fromisoformat(
            time
        )  # преобразуем строку в datetime формата ISO 8601
    except ValueError:
        raise InvalidTimeMarkerError(
            f"Ошибка: в файле {file_number} в строке {line_number} неправильно указано timestamp"
        )
    if (
        timestamp.tzinfo is None
    ):  # если не указан часовой пояс, то приводим все к aware (с часовым поясом)
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp


def check_and_create_event_parser(
    raw: Mapping[str, Any], file_number: int, line_number: int
) -> Event:
    for field in AVAILABLE_FIELDS:
        if field not in raw:
            raise InvalidEventError(
                f"Ошибка: в файле {file_number} в строке {line_number} нет обязательного поля {field}"
            )

        total = raw.get(field)
        if total is None:
            raise InvalidEventError(
                f"Ошибка: в файле {file_number} в строке {line_number} нет обязательного поля {field}"
            )
        if not isinstance(total, str):
            raise InvalidEventError(
                f"Ошибка: в файле {file_number} в строке {line_number} поле {field} должно быть строкой"
            )

    try:
        timestamp = check_and_create_timestamp(
            raw["timestamp"], file_number, line_number
        )
    except InvalidTimeMarkerError:
        raise

    try:
        level = Level(raw["level"])
    except ValueError:
        raise InvalidEventError(
            f"Ошибка: в файле {file_number} в строке {line_number} неизвестный level"
        )

    source = raw["source"]
    if source.strip() == "":
        raise InvalidEventError(
            f"Ошибка: в файле {file_number} в строке {line_number} source пустой"
        )

    message = raw["message"]

    event = Event(timestamp, level, source, message)
    return event
