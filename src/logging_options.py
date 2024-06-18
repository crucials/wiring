import logging
from typing import Optional, TypedDict


class LoggingOptions(TypedDict):
    handler: Optional[logging.Handler]
    level: int


DEFAULT_LOGGING_OPTIONS: LoggingOptions = {'handler': None, 'level': logging.WARNING}
