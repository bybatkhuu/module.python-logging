# -*- coding: utf-8 -*-

import os
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
