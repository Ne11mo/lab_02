import json
from pathlib import Path
from typing import Any


def write_report(report: dict[str, Any], output_data_file: Path) -> None:
    """
    This function writes the report into users file or REPORT.json
    :param report: dict[str, Any]
    :param output_data_file: Path
    :return None
    """

    with output_data_file.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")
