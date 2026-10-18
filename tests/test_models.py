from datetime import UTC, datetime

import pytest

from streamstats.errors import InvalidTimeMarkerError
from streamstats.models import (
    Event,
    Level,
    check_and_create_event_parser,
    check_and_create_timestamp,
)

timestamp1 = "2026-10-17T08:00:00"
timestamp2 = "2026-12-31 23:59:59+03:00"
negative_timestamp1 = "2026-13-01T08:00:00"
negative_timestamp2 = "2026-12-33T08:00:00"
negative_timestamp3 = "2026-12-31T28:00:00"

level_info = Level.INFO
level_warning = Level.WARNING
level_error = Level.ERROR


def test_create_event_parser() -> None:
    raw1 = {
        "timestamp": timestamp1,
        "level": "INFO",
        "source": "ababa",
        "message": "www",
    }
    event1 = Event(
        timestamp=datetime.fromisoformat(timestamp1).replace(tzinfo=UTC),
        level=level_info,
        source="ababa",
        message="www",
    )
    raw2 = {
        "timestamp": timestamp2,
        "level": "ERROR",
        "source": "yandex",
        "message": "Thank you for report",
    }
    event2 = Event(
        timestamp=datetime.fromisoformat(timestamp2),
        level=level_error,
        source="yandex",
        message="Thank you for report",
    )
    raw3 = {
        "timestamp": timestamp2,
        "level": "WARNING",
        "source": "Dima",
        "message": "Go buhat",
    }
    event3 = Event(
        timestamp=datetime.fromisoformat(timestamp2),
        level=level_warning,
        source="Dima",
        message="Go buhat",
    )

    assert check_and_create_event_parser(raw1, 1, 0) == event1
    assert check_and_create_event_parser(raw2, 1, 0) == event2
    assert check_and_create_event_parser(raw3, 1, 0) == event3


def test_invalid_time_marker_error() -> None:
    with pytest.raises(InvalidTimeMarkerError):
        check_and_create_timestamp(negative_timestamp1, 0, 0)
    with pytest.raises(InvalidTimeMarkerError):
        check_and_create_timestamp(negative_timestamp2, 0, 0)
    with pytest.raises(InvalidTimeMarkerError):
        check_and_create_timestamp(negative_timestamp3, 0, 0)
