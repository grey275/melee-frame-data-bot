import os
import logging


def getPath(_file):
    return os.path.join(os.path.dirname(__file__), _file)


my_logger = logging.getLogger('framedata-bot')  #
my_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s '
                              '| %(name)s | %(message)s')

error_handler = logging.FileHandler(getPath('errors.log'))
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

debug_handler = logging.StreamHandler()
debug_handler.setLevel(logging.DEBUG)

info_handler = logging.FileHandler(getPath('info.log'))
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

active_handlers = [
    error_handler,
    debug_handler,
    info_handler,
    ]

for handler in active_handlers:
    my_logger.addHandler(handler)
