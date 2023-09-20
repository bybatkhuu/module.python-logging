# -*- coding: utf-8 -*-

import pydantic

if "2.0.0" <= pydantic.__version__:
    from .config import LoggerConfigPM
else:
    from .config_v1 import LoggerConfigPM
