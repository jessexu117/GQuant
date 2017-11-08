# -*- coding: utf-8 -*-

"""
A Simple Logger Module

@author: Jesse J. Hsu
@email: jinjie.xu@whu.edu.cn 
@version: 0.1
"""

import os
import logging

from ..conf import LOG, OUT_PATH


def simple_logger(to_file=LOG['TO_FILE']):
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(LOG['ROOT_LEVEL'])

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # create file handler
    if to_file:
        file_handler = logging.FileHandler(os.path.join(OUT_PATH, 'trade_log.log'), mode='w')
        file_handler.setLevel(LOG['FILE_LEVEL'])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # create stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(LOG['CONSOLE_LEVEL'])
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
