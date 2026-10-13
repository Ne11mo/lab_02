from collections.abc import Iterable
from pathlib import Path

from src.streamstats.errors import InvalidFilePathError


def check_input_data_files(input_data_files: Iterable[Path]) -> None:
    for file_path in input_data_files:
        if not file_path.is_file():
            raise InvalidFilePathError(
                "Неправильный путь к файлу или несуществующий файл"
            )


def validate_data(args) -> None:
    input_data_files = args.input_data_files
    check_input_data_files(input_data_files)
