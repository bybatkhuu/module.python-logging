# -*- coding: utf-8 -*-

import os
import copy
import errno

# import logging

from pydantic import validate_call
from loguru import logger

# logger = logging.getLogger(__name__)


@validate_call
def create_dir(create_dir: str, quiet: bool = True):
    """Create directory if `create_dir` doesn't exist.

    Args:
        create_dir (str , required): Create directory path.
        quiet      (bool, optional): If True, don't log anything unless debug is enabled. Defaults to True.
    """

    if not os.path.isdir(create_dir):
        try:
            if quiet:
                logger.debug(f"Creaing '{create_dir}' directory...")
            else:
                logger.info(f"Creaing '{create_dir}' directory...")

            os.makedirs(create_dir)
        except OSError as err:
            if err.errno == errno.EEXIST:
                logger.debug(f"'{create_dir}' directory already exists!")
            else:
                logger.error(f"Failed to create '{create_dir}' directory!")
                raise

        if quiet:
            logger.debug(f"Successfully created '{create_dir}' directory.")
        else:
            logger.success(f"Successfully created '{create_dir}' directory.")


@validate_call
def deep_merge(dict1: dict, dict2: dict) -> dict:
    """Return a new dictionary that's the result of a deep merge of two dictionaries.
    If there are conflicts, values from `dict2` will overwrite those in `dict1`.

    Args:
        dict1 (dict, required): The base dictionary that will be merged.
        dict2 (dict, required): The dictionary to merge into `dict1`.

    Returns:
        dict: The merged dictionary.
    """

    _merged = copy.deepcopy(dict1)
    for _key, _val in dict2.items():
        if (
            _key in _merged
            and isinstance(_merged[_key], dict)
            and isinstance(_val, dict)
        ):
            _merged[_key] = deep_merge(_merged[_key], _val)
        else:
            _merged[_key] = copy.deepcopy(_val)

    return _merged
