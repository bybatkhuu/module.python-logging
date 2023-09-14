# -*- coding: utf-8 -*-

from beans_logging import Logger, LoggerLoader
from beans_logging.fastapi import add_http_file_handler, add_http_file_json_handler


logger_loader = LoggerLoader()
logger: Logger = logger_loader.load()

if logger_loader.config.extra.http_file_enabled:
    add_http_file_handler(
        logger_loader=logger_loader,
        log_path=logger_loader.config.extra.http_log_path,
        err_path=logger_loader.config.extra.http_err_path,
    )

if logger_loader.config.extra.http_json_enabled:
    add_http_file_json_handler(
        logger_loader=logger_loader,
        log_path=logger_loader.config.extra.http_json_path,
        err_path=logger_loader.config.extra.http_json_err_path,
    )
