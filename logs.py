import logging
import os


class ExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record):
        s = super().format(record)
        if record.exc_text:
            s = s.replace('\n', '\n\t') + '\n'
        return s


exception_format = ExceptionFormatter('%(asctime)s|%(levelname)s|%(message)s',
                                      '%m/%d/%Y %I:%M:%S %p')

my_logger = logging.getLogger("framedata-bot")
my_logger.setLevel(logging.DEBUG)

error_handler = logging.FileHandler(filename="errors.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(exception_format)

debug_handler = logging.StreamHandler()
debug_handler.setLevel(logging.DEBUG)

analytics_handler = logging.FileHandler('analytics.log')
analytics_handler.setLevel(logging.INFO)
analytics_formatter = logging.Formatter("%(asctime)s\n%(message)s\n")
analytics_handler.setFormatter(analytics_formatter)

handlers = [
    error_handler,
    debug_handler,
    analytics_handler,
    ]

for handler in handlers:
    my_logger.addHandler(handler)
