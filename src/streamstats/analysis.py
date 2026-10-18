from collections.abc import Iterable
from typing import Any

from .models import Event, Level, ParserStatistics


def make_top_5_source(errors_sources: dict[str, int]) -> dict[str, int]:
    """
    This function makes top 5 errors sources
    :param errors_sources: dict[str, int]
    :return dict[str, int]
    """

    top_5_source = []
    for error_source, value in errors_sources.values():
        top_5_source.append((error_source, value))

    top_5_source.sort(key=lambda x: (-x[1], x[0]))

    result = {}
    for i in range(min(5, len(top_5_source))):
        result[top_5_source[i][0]] = top_5_source[i][1]
    return result


def start_analyze(
    events: Iterable[Event], parser_statistics: ParserStatistics
) -> dict[str, Any]:
    """
    This function analyzes events and makes statistics
    :param events: Iterable[Event]
    :param parser_statistics: ParserStatistics
    :return dict[str, Any]
    """

    statistics: dict = {
        "all_events_count": 0,
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }
    sources = {}
    errors_sources = {}
    min_timestamp, max_timestamp = None, None
    for event in events:
        statistics["all_events_count"] += 1
        statistics[event.level.value] += 1

        if event.source not in sources:
            sources[event.source] = 0
        sources[event.source] += 1

        if event.level == Level.ERROR or event.level == Level.CRITICAL:
            if event.source not in errors_sources:
                errors_sources[event.source] = 0

            errors_sources[event.source] += 1

        if min_timestamp is None:
            min_timestamp = event.timestamp
        else:
            min_timestamp = min(min_timestamp, event.timestamp)

        if max_timestamp is None:
            max_timestamp = event.timestamp
        else:
            max_timestamp = max(max_timestamp, event.timestamp)

    statistics["events_from_every_sources"] = sources

    top_5_source = make_top_5_source(errors_sources)
    statistics["top_error_sources"] = top_5_source

    if min_timestamp is None:
        statistics["min_timestamp"] = None
    else:
        statistics["min_timestamp"] = min_timestamp.isoformat()
    if max_timestamp is None:
        statistics["max_timestamp"] = None
    else:
        statistics["max_timestamp"] = max_timestamp.isoformat()

    statistics["skipped_lines"] = parser_statistics.skipped_lines

    return statistics
