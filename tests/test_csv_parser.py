from datetime import UTC, datetime
from pathlib import Path

import pytest

from streamstats.errors import InvalidEventError, InvalidTimeMarkerError
from streamstats.models import Level, ParserStatistics
from streamstats.parsers import start_csv_parser


def test_csv_parser(tmp_path: Path) -> None:
    path = tmp_path / "test.csv"
    path.write_text(
        "timestamp,level,source,message\n2026-12-31T10:00:00,WARNING,yandex,hello\n",
        encoding="utf-8",
    )

    events = list(start_csv_parser([path], False, ParserStatistics()))
    assert len(events) == 1
    assert events[0].timestamp == datetime.fromisoformat("2026-12-31T10:00:00").replace(
        tzinfo=UTC
    )
    assert events[0].level == Level.WARNING
    assert events[0].source == "yandex"
    assert events[0].message == "hello"


def test_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "test.csv"
    path.write_text("", encoding="utf-8")

    events = list(start_csv_parser([path], False, ParserStatistics()))
    assert len(events) == 0


def test_only_titles(tmp_path: Path) -> None:
    path = tmp_path / "test.csv"
    path.write_text("timestamp,level,source,message\n", encoding="utf-8")

    events = list(start_csv_parser([path], False, ParserStatistics()))
    assert len(events) == 0


def test_several_files(tmp_path: Path) -> None:
    path1 = tmp_path / "test1.csv"
    path2 = tmp_path / "test2.csv"

    path1.write_text(
        "timestamp,level,source,message\n2026-12-31T10:00:00,WARNING,yandex,hello\n",
        encoding="utf-8",
    )
    path2.write_text(
        "timestamp,level,source,message\n2027-10-17T17:00:00+03:00,DEBUG,nikita,dr",
        encoding="utf-8",
    )

    events = list(start_csv_parser([path1, path2], False, ParserStatistics()))
    assert len(events) == 2
    assert events[0].level == Level.WARNING
    assert events[0].source == "yandex"
    assert events[1].level == Level.DEBUG
    assert events[1].source == "nikita"


def test_unicode(tmp_path: Path) -> None:
    path = tmp_path / "test.csv"
    path.write_text(
        'timestamp,level,source,message\n2026-12-31T10:00:00,WARNING,neighbour🤡,"Привет, друг!"\n',
        encoding="utf-8",
    )

    events = list(start_csv_parser([path], False, ParserStatistics()))

    assert len(events) == 1
    assert events[0].source == "neighbour🤡"
    assert events[0].message == "Привет, друг!"


def test_invalid_title(tmp_path: Path) -> None:
    path = tmp_path / "test.csv"
    path.write_text("timestamp,bad,source,message\n", encoding="utf-8")

    with pytest.raises(InvalidEventError):
        list(start_csv_parser([path], False, ParserStatistics()))


def test_invalid_event_error_1(tmp_path: Path) -> None:
    path = tmp_path / "test.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-12-31T10:00:00,WARNING,yandex,thank you\n"
        "2026-10-17T08:00:00,yandex,thank you\n",
        encoding="utf-8",
    )

    statistic = ParserStatistics()

    events = list(start_csv_parser([path], True, statistic))
    assert len(events) == 1
    assert statistic.skipped_lines == 1

    with pytest.raises(InvalidEventError):
        list(start_csv_parser([path], False, ParserStatistics()))


def test_invalid_event_error_2(tmp_path: Path) -> None:
    path = tmp_path / "test.csv"
    path.write_text(
        "timestamp,level,source,message\nвчера,INFO,home,hey", encoding="utf-8"
    )

    statistic = ParserStatistics()
    events = list(start_csv_parser([path], True, statistic))

    assert len(events) == 0
    assert statistic.skipped_lines == 1

    with pytest.raises(InvalidTimeMarkerError):
        list(start_csv_parser([path], False, ParserStatistics()))


def test_invalid_event_error_3(tmp_path: Path) -> None:
    path = tmp_path / "test.csv"
    path.write_text(
        "timestamp,level,source,message\n2026-10-17 03:00:00,INFO,,hey",
        encoding="utf-8",
    )

    statistic = ParserStatistics()
    events = list(start_csv_parser([path], True, statistic))

    assert len(events) == 0
    assert statistic.skipped_lines == 1

    with pytest.raises(InvalidEventError):
        list(start_csv_parser([path], False, ParserStatistics()))
