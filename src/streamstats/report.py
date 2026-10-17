import json
import sys
from pathlib import Path
from typing import Any


def write_report(report: dict[str, Any], output_data_file: Path | None) -> None:
    if output_data_file is None:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return

    with output_data_file.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")
