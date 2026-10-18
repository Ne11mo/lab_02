import csv
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
    if output_data_file.suffix.lower() == ".json":
        with output_data_file.open("w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            f.write("\n")

    else:
        with output_data_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["field", "key", "value"])

            for key, value in report.items():
                if isinstance(value, dict):
                    for f_key, f_value in value.items():
                        writer.writerow([key, f_key, f_value])
                else:
                    writer.writerow([key, "-", value])
