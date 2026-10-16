from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from .errors import InvalidEventError, InvalidFilePathError, InvalidTimeMarkerError

AVAILABLE_FIELDS = {
    "timestamp",
    "level",
    "source",
    "message",
}  # множество обязательных полей


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


def check_input_paths_of_files(input_data_files: Iterable[Path]) -> None:
    for file_path in input_data_files:
        if not file_path.is_file():
            raise InvalidFilePathError(
                "Неправильный путь к файлу или несуществующий файл"
            )


def check_and_create_timestamp_(time: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(
            time
        )  # преобразуем строку в datetime формата ISO 8601
    except ValueError:
        raise InvalidTimeMarkerError
    if (
        timestamp.tzinfo is None
    ):  # если не указан часовой пояс, то приводим все к aware (с часовым поясом)
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp


# добавить в исключения возврат номера файла и номера строки
def check_and_create_event_parser(raw: Mapping[str, Any]) -> Event:
    for field in AVAILABLE_FIELDS:
        if field not in raw:
            raise InvalidEventError(f"Нет обязательного поля {field}")

        total = raw.get(field)
        if total is None:
            raise InvalidEventError(f"Нет обязательного поля {field}")
        if not isinstance(total, str):
            raise InvalidEventError(f"Поле {field} должно быть строкой")

    try:
        timestamp = check_and_create_timestamp_(raw["timestamp"])
    except InvalidTimeMarkerError:
        raise InvalidTimeMarkerError("Неправильно указано timestamp")

    try:
        level = Level(raw["level"])
    except ValueError:
        raise InvalidEventError("Неизвестный level")

    source = raw["source"]
    if source.strip() == "":
        raise InvalidEventError("Source пустой")

    message = raw["message"]

    event = Event(timestamp, level, source, message)
    return event
