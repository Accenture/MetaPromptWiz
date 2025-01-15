import json
import logging
from time import time
from typing import List, Any, Dict
import os

class MyHandler(logging.Handler):
    """
    does all the following:
    * adds time taken to each log
    * saves logs in a list that is a global variable
    * writes logs in a file
    """

    def __init__(self, log_list: List[Any], log_filepath: str = 'config_wiz_logs.json'):
        super().__init__()
        self.log_list: List[Dict[str, str | float]] = log_list
        self.log_filepath = log_filepath
        self.prev_time = time()
        if os.path.exists(self.log_filepath):
            os.remove(self.log_filepath)

    def emit(self, record):
        # add time taken to the log
        message: str = json.dumps(self.format(record))
        new_time = time()
        final_log: Dict[str, Any] = {'level': record.levelname, 'message': message, 'time': round(new_time - self.prev_time, 2)}
        self.prev_time = new_time
        # add log to the list
        self.log_list.append(final_log)
        # write updated log_list to the file
        with open(self.log_filepath, 'w') as f:
            json.dump(log_list, f, indent=4)


def setup_logger() -> None:
    """
    almost entirely copied from here https://docs.python.org/3/howto/logging.html
    :return: logger
    """
    global logger, log_list
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # handler that would format the logs and save them in a list
    handler = MyHandler(log_list)

    # create formatter to the handler
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    # add handler to the logger
    logger.addHandler(handler)

    handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)


log_list: List[Dict[str, Any]] = list()
logger: logging.Logger
setup_logger()

