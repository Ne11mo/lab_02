class  StreamStatsError(Exception):
    """Base Stream Stats Error"""


class InvalidFormatError(StreamStatsError):
    pass


class InvalidTimeMarkerError(StreamStatsError):
    pass


class InvalidEventError(StreamStatsError):
    pass


class ConfigurationCLIError(StreamStatsError):
    pass