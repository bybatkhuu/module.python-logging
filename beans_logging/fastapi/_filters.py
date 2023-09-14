# -*- coding: utf-8 -*-

from beans_logging.filters import use_all_filter


def use_http_filter(record: dict) -> bool:
    """Filter message only for http access log handler by checking 'http_info' key in extra.

    Args:
        record (dict): Log record as dictionary.

    Returns:
        bool: True if record has 'http_info' key in extra, False otherwise.
    """

    if not use_all_filter(record):
        return False

    if "http_info" not in record["extra"]:
        return False

    return True
