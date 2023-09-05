# -*- coding: utf-8 -*-

import os
import sys
import datetime
from enum import Enum
from typing import List

from pydantic import (
    BaseModel,
    constr,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
)


class LevelEnum(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StdHandlerPM(BaseModel):
    enabled: bool = Field(default=True)

    model_config = ConfigDict(extra="allow")


class StreamPM(BaseModel):
    use_color: bool = Field(default=True)
    use_icon: bool = Field(default=False)
    format_str: constr(strip_whitespace=True) = Field(
        default="[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{level_short:<5}</level> | <w>{name}:{line}</w>]: <level>{message}</level>",
        min_length=9,
    )
    std_handler: StdHandlerPM = Field(default=StdHandlerPM())

    model_config = ConfigDict(extra="allow")


class LogHandlersPM(BaseModel):
    enabled: bool = Field(default=False)
    format_str: constr(strip_whitespace=True) = Field(
        default="[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level_short:<5} | {name}:{line}]: {message}",
        min_length=9,
    )
    log_path: constr(strip_whitespace=True) = Field(
        default="{app_name}.std.all.log", min_length=5, max_length=255
    )
    err_path: constr(strip_whitespace=True) = Field(
        default="{app_name}.std.err.log", min_length=5, max_length=255
    )

    @model_validator(mode="after")
    def _check_log_path(self) -> "LogHandlersPM":
        if self.log_path == self.err_path:
            raise ValueError(
                f"`log_path` and `err_path` attributes are same: '{self.log_path}', must be different!"
            )

        return self

    model_config = ConfigDict(extra="allow")


class JsonHandlersPM(BaseModel):
    enabled: bool = Field(default=False)
    use_custom: bool = Field(default=False)
    log_path: constr(strip_whitespace=True) = Field(
        default="{app_name}.json.all.log", min_length=5, max_length=255
    )
    err_path: constr(strip_whitespace=True) = Field(
        default="{app_name}.json.err.log", min_length=5, max_length=255
    )

    @model_validator(mode="after")
    def _check_log_path(self) -> "JsonHandlersPM":
        if self.log_path == self.err_path:
            raise ValueError(
                f"`log_path` and `err_path` attributes are same: '{self.log_path}', must be different!"
            )

        return self

    model_config = ConfigDict(extra="allow")


class FilePM(BaseModel):
    logs_dir: str = Field(
        default=os.path.join(os.getcwd(), "logs"), min_length=2, max_length=4096
    )
    rotate_size: int = Field(
        default=10_000_000, ge=1_000, lt=1_000_000_000  # 10MB = 10 * 1000 * 1000
    )
    rotate_time: datetime.time = Field(datetime.time(0, 0, 0))
    backup_count: int = Field(default=90, ge=1)
    encoding: constr(strip_whitespace=True) = Field(
        default="utf8", min_length=2, max_length=31
    )
    log_handlers: LogHandlersPM = Field(default=LogHandlersPM())
    json_handlers: JsonHandlersPM = Field(default=JsonHandlersPM())

    @field_validator("rotate_time", mode="before")
    @classmethod
    def _check_rotate_time(cls, val):
        if isinstance(val, str):
            val = datetime.time.fromisoformat(val)
        return val

    model_config = ConfigDict(extra="allow")


class AutoLoadPM(BaseModel):
    enabled: bool = Field(default=True)
    only_base: bool = Field(default=False)
    ignore_modules: List[str] = Field(default=[])

    model_config = ConfigDict(extra="allow")


class InterceptPM(BaseModel):
    auto_load: AutoLoadPM = Field(default=AutoLoadPM())
    include_modules: List[str] = Field(default=[])
    mute_modules: List[str] = Field(default=[])

    model_config = ConfigDict(extra="allow")


class ExtraPM(BaseModel):
    model_config = ConfigDict(extra="allow")


class LoggerConfigPM(BaseModel):
    app_name: constr(strip_whitespace=True) = Field(
        default=os.path.splitext(os.path.basename(sys.argv[0]))[0]
        .strip()
        .replace(" ", "_")
        .lower(),
        min_length=1,
        max_length=127,
    )
    level: LevelEnum = Field(default=LevelEnum.INFO)
    use_backtrace: bool = Field(default=True)
    use_diagnose: bool = Field(default=False)
    stream: StreamPM = Field(default=StreamPM())
    file: FilePM = Field(default=FilePM())
    intercept: InterceptPM = Field(default=InterceptPM())
    extra: ExtraPM = Field(default=ExtraPM())

    @model_validator(mode="after")
    def _check_log_path(self) -> "LoggerConfigPM":
        if "{app_name}" in self.file.log_handlers.log_path:
            self.file.log_handlers.log_path = self.file.log_handlers.log_path.format(
                app_name=self.app_name
            )

        if "{app_name}" in self.file.log_handlers.err_path:
            self.file.log_handlers.err_path = self.file.log_handlers.err_path.format(
                app_name=self.app_name
            )

        if "{app_name}" in self.file.json_handlers.log_path:
            self.file.json_handlers.log_path = self.file.json_handlers.log_path.format(
                app_name=self.app_name
            )

        if "{app_name}" in self.file.json_handlers.err_path:
            self.file.json_handlers.err_path = self.file.json_handlers.err_path.format(
                app_name=self.app_name
            )

        return self

    model_config = ConfigDict(extra="allow")
