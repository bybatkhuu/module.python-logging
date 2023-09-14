# -*- coding: utf-8 -*-

from pydantic import validate_call

from beans_logging import LoggerLoader

from ._filters import use_http_filter
from ._formats import http_file_format, http_file_json_format


@validate_call(config=dict(arbitrary_types_allowed=True))
def add_http_file_handler(
    logger_loader: LoggerLoader,
    log_path: str = "http/{app_name}.http.access.log",
    err_path: str = "http/{app_name}.http.err.log",
):
    """Add http access log file and error file handler.

    Args:
        logger_loader (LoggerLoader, required): LoggerLoader instance.
        log_path      (str,          optional): Log file path. Defaults to "http/{app_name}.http.access.log".
        err_path      (str,          optional): Error log file path. Defaults to "http/{app_name}.http.err.log".
    """

    logger_loader.add_custom_handler(
        handler_name="FILE.HTTP",
        sink=log_path,
        filter=use_http_filter,
        format=http_file_format,
    )

    logger_loader.add_custom_handler(
        handler_name="FILE.HTTP_ERR",
        sink=err_path,
        level="WARNING",
        filter=use_http_filter,
        format=http_file_format,
    )


@validate_call(config=dict(arbitrary_types_allowed=True))
def add_http_file_json_handler(
    logger_loader: LoggerLoader,
    log_path: str = "json.http/{app_name}.json.http.access.log",
    err_path: str = "json.http/{app_name}.json.http.err.log",
):
    """Add http access json log file and json error file handler.

    Args:
        logger_loader (LoggerLoader, required): LoggerLoader instance.
        log_path      (str,          optional): Json log file path. Defaults to "http.json/{app_name}.json.http.access.log".
        err_path      (str,          optional): Json error log file path. Defaults to "http.json/{app_name}.json.http.err.log".
    """

    logger_loader.add_custom_handler(
        handler_name="FILE.JSON.HTTP",
        sink=log_path,
        filter=use_http_filter,
        format=http_file_json_format,
    )

    logger_loader.add_custom_handler(
        handler_name="FILE.JSON.HTTP_ERR",
        sink=err_path,
        level="WARNING",
        filter=use_http_filter,
        format=http_file_json_format,
    )