import os
import time
import sys
import codecs
import fcntl
import logging
import pathlib

from logging.handlers import TimedRotatingFileHandler

FORMAT = '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s'


class MultiProcessSafeHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, utc=False):
        TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, True, utc)
        self.current_file_name = self.get_new_file_name()
        self.lock_file = None

    def get_new_file_name(self):
        return self.baseFilename + "." + time.strftime(self.suffix, time.localtime()) + ".log"

    def shouldRollover(self, record):
        if self.current_file_name != self.get_new_file_name():
            return True
        return False

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.current_file_name = self.get_new_file_name()
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

    def _open(self):
        if self.encoding is None:
            stream = open(self.current_file_name, self.mode)
        else:
            stream = codecs.open(self.current_file_name, self.mode, self.encoding)
        return stream

    def acquire(self):
        self.lock_file = open(self.baseFilename + ".lock", "w")
        fcntl.lockf(self.lock_file, fcntl.LOCK_EX)

    def release(self):
        if self.lock_file:
            self.lock_file.close()
            self.lock_file = None


def init_stream_handler():
    fmt = logging.Formatter(FORMAT)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)

    return handler


def init_file_handler(log_filename):
    log_filepath = pathlib.Path(log_filename)
    if log_filepath.suffix == '.log':
        log_filename = log_filename.replace('.log', '')

    fmt = logging.Formatter(FORMAT)
    handler = MultiProcessSafeHandler(
        filename=log_filename,
        when='midnight',
        backupCount=180,
        encoding='utf-8'
    )
    handler.setFormatter(fmt)

    return handler


def get_logger(name, log_filename):
    init_logger = logging.getLogger(name)

    init_logger.addHandler(init_stream_handler())
    if log_filename is not None:
        init_logger.addHandler(init_file_handler(log_filename))
    init_logger.setLevel(logging.INFO)

    return init_logger
