# -*- coding: utf-8 -*-

import os
from typing import Union

from loguru import logger
from loguru._logger import Logger

from ._base import LoggerLoader
from .__version__ import __version__

logger_loader: Union[LoggerLoader, None] = None
_DISABLE_DEFAULT_LOGGER = (
    str(os.getenv("BEANS_LOGGING_DISABLE_DEFAULT")).strip().lower()
)
if (_DISABLE_DEFAULT_LOGGER != "true") and (_DISABLE_DEFAULT_LOGGER != "1"):
    logger_loader: LoggerLoader = LoggerLoader()
    logger: Logger = logger_loader.load()
