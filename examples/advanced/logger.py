# -*- coding: utf-8 -*-

from beans_logging import LoggerLoader, Logger
from beans_logging.fastapi import add_file_http_handler, add_file_json_http_handler


logger_loader = LoggerLoader()
logger: Logger = logger_loader.load()

add_file_http_handler(
    logger_loader=logger_loader,
    log_path=logger_loader.config.extra.http_log_path,
    err_path=logger_loader.config.extra.http_err_path,
)
add_file_json_http_handler(
    logger_loader=logger_loader,
    log_path=logger_loader.config.extra.http_json_path,
    err_path=logger_loader.config.extra.http_json_err_path,
)
