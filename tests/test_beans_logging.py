# -*- coding: utf-8 -*-

import pytest

from beans_logging._schema import LoggerConfigPM
from beans_logging.auto import logger, Logger, LoggerLoader


@pytest.fixture
def logger_loader():
    _logger_loader = LoggerLoader()

    yield _logger_loader

    del _logger_loader


def test_init(logger_loader):
    logger.info("Testing initialization of 'LoggerLoader'...")

    assert isinstance(logger_loader, LoggerLoader)
    assert logger_loader.handlers_map == {"default": 0}
    assert logger_loader.configs_dir == LoggerLoader._CONFIGS_DIR
    assert logger_loader.config_filename == LoggerLoader._CONFIG_FILENAME
    assert isinstance(logger_loader.config, LoggerConfigPM)

    logger.success("Done: Initialization of 'LoggerLoader'.")


def test_load(logger_loader):
    logger.info("Testing 'load' method of 'LoggerLoader'...")

    logger_loader.update_config(config={"level": "TRACE"})
    _logger: Logger = logger_loader.load()

    assert isinstance(_logger, Logger)
    assert _logger == logger
    _logger.trace("Tracing...")
    _logger.debug("Debugging...")
    _logger.info("Logging info.")
    _logger.success("Success.")
    _logger.warning("Warning something.")
    _logger.error("Error occured.")
    _logger.critical("CRITICAL ERROR.")

    logger.success("Done: 'load' method.")


def test_methods():
    logger.info("Testing 'logger' methods...")

    logger.trace("Tracing...")
    logger.debug("Debugging...")
    logger.info("Logging info.")
    logger.success("Success.")
    logger.warning("Warning something.")
    logger.error("Error occured.")
    logger.critical("CRITICAL ERROR.")

    logger.success("Done: 'logger' methods.")
