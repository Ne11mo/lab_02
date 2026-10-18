import json
import subprocess


def test_cli_csv(tmp_path):
    path = tmp_path / "test.csv"
    report_path = tmp_path / "report.json"

    path.write_text(
        "timestamp,level,source,message\n2026-10-17T08:00:00,CRITICAL,yandex,error\n2026-12-31 10:00:00+03:00,INFO,calendar,new year\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python",
            "-m",
            "streamstats",
            "analyze",
            str(path),
            "--format",
            "csv",
            "--output",
            str(report_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["all_events_count"] == 2
    assert report["skipped_lines"] == 0
    assert report["CRITICAL"] == 1


def test_cli_json(tmp_path):
    path = tmp_path / "test.json"
    report_path = tmp_path / "report.json"
    raw1 = {
        "timestamp": "2026-10-17T08:00:00",
        "level": "WARNING",
        "source": "Dima",
        "message": "Привет !!!",
    }
    raw2 = {
        "timestamp": "2026-12-31T10:00:00+03:00",
        "level": "BAD",
        "source": "yandex",
        "message": "STOP",
    }

    line1 = json.dumps(raw1, ensure_ascii=False)
    line2 = json.dumps(raw2, ensure_ascii=False)
    path.write_text(line1 + "\n" + line2 + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            "python",
            "-m",
            "streamstats",
            "analyze",
            str(path),
            "--format",
            "jsonl",
            "--output",
            str(report_path),
            "--skip-invalid",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["all_events_count"] == 1
    assert report["skipped_lines"] == 1
    assert report["WARNING"] == 1
