# -*- coding: utf-8 -*-

from enum import Enum


class WarnEnum(str, Enum):
    RAISE = "RAISE"
    LOG = "LOG"
    DEBUG = "DEBUG"
    IGNORE = "IGNORE"
