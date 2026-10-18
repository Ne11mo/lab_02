import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from streamstats.errors import InvalidEventError
from streamstats.models import Level, ParserStatistics
from streamstats.parsers import start_jsonl_parser


def make_jsonl(list_of_dicts: list):
    list_of_jsonl_events = []
    for d in list_of_dicts:
        list_of_jsonl_events.append(json.dumps(d, ensure_ascii=False))

    return "\n".join(list_of_jsonl_events) + "\n"


def test_start_jsonl_parser(tmp_path: Path):
    path = tmp_path / "test.jsonl"
    row = {
        "timestamp": "2026-10-17T08:00:00+03:00",
        "level": "ERROR",
        "source": "yandex",
        "message": "hello",
    }
    path.write_text(make_jsonl([row]), encoding="utf-8")

    statistic = ParserStatistics()
    events = list(start_jsonl_parser([path], False, statistic))

    assert len(events) == 1
    assert events[0].timestamp == datetime.fromisoformat("2026-10-17T08:00:00+03:00")
    assert events[0].level == Level.ERROR
    assert events[0].source == "yandex"
    assert events[0].message == "hello"
    assert statistic.skipped_lines == 0


def test_empty_file(tmp_path: Path):
    path = tmp_path / "test.jsonl"
    path.write_text("", encoding="utf-8")

    statistic = ParserStatistics()
    events = list(start_jsonl_parser([path], False, statistic))

    assert len(events) == 0
    assert statistic.skipped_lines == 0


def test_invalid_event_error_1(tmp_path: Path):
    path = tmp_path / "test.jsonl"
    row = {
        "timestamp": "2026-10-17T08:00:00+03:00",
        "source": "yandex",
        "message": "hello",
    }
    path.write_text(make_jsonl([row]), encoding="utf-8")

    statistic = ParserStatistics()
    events = list(start_jsonl_parser([path], True, statistic))

    assert len(events) == 0
    assert statistic.skipped_lines == 1

    with pytest.raises(InvalidEventError):
        list(start_jsonl_parser([path], False, statistic))


def test_invalid_event_error_2(tmp_path: Path):
    path = tmp_path / "test.jsonl"
    row = {
        "timestamp": "2026-10-17T08:00:00+03:00",
        "level": "Bad",
        "source": "yandex",
        "message": "hello",
    }
    path.write_text(make_jsonl([row]), encoding="utf-8")

    statistic = ParserStatistics()
    events = list(start_jsonl_parser([path], True, statistic))

    assert len(events) == 0
    assert statistic.skipped_lines == 1

    with pytest.raises(InvalidEventError):
        list(start_jsonl_parser([path], False, statistic))


def test_invalid_event_error_3(tmp_path: Path):
    path = tmp_path / "test.jsonl"
    row = {
        "timestamp": "2026-10-17T08:00:00+03:00",
        "level": "INFO",
        "source": "",
        "message": "hello",
    }
    path.write_text(make_jsonl([row]), encoding="utf-8")

    statistic = ParserStatistics()
    events = list(start_jsonl_parser([path], True, statistic))

    assert len(events) == 0
    assert statistic.skipped_lines == 1

    with pytest.raises(InvalidEventError):
        list(start_jsonl_parser([path], False, statistic))


def test_several_files(tmp_path: Path):
    path1 = tmp_path / "test1.jsonl"
    path2 = tmp_path / "test2.jsonl"

    row1 = {
        "timestamp": "2026-10-17T08:00:00+03:00",
        "level": "ERROR",
        "source": "yandex",
        "message": "hello",
    }
    row2 = {
        "timestamp": "2026-12-31 18:00:00",
        "level": "WARNING",
        "source": "nikita",
        "message": "thank you",
    }

    path1.write_text(make_jsonl([row1]), encoding="utf-8")
    path2.write_text(make_jsonl([row2]), encoding="utf-8")

    statistic = ParserStatistics()

    events = list(start_jsonl_parser([path1, path2], True, statistic))

    assert len(events) == 2
    assert statistic.skipped_lines == 0
    assert events[0].timestamp == datetime.fromisoformat("2026-10-17T08:00:00+03:00")
    assert events[0].level == Level.ERROR
    assert events[0].source == "yandex"
    assert events[0].message == "hello"
    assert events[1].timestamp == datetime.fromisoformat("2026-12-31 18:00:00").replace(
        tzinfo=UTC
    )
    assert events[1].level == Level.WARNING
    assert events[1].source == "nikita"
    assert events[1].message == "thank you"


def test_unicode(tmp_path: Path):
    path = tmp_path / "test.jsonl"
    row = {
        "timestamp": "2026-10-17T08:00:00",
        "level": "ERROR",
        "source": "neighbour🤡",
        "message": "Привет, друг!",
    }
    path.write_text(make_jsonl([row]), encoding="utf-8")

    events = list(start_jsonl_parser([path], False, ParserStatistics()))
    assert len(events) == 1
    assert events[0].source == "neighbour🤡"
    assert events[0].message == "Привет, друг!"
