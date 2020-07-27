# -*- coding: utf-8 -*-
import sys
import io
import traceback
import logging
import logging.config
import logging.handlers
from pathlib import Path

class logger:
    def __init__(self, name, path, rotateWen, lotateCount, encoding = "utf-8"):
        p = Path(path)
        if not p.is_absolute():
            p = Path(Path(__file__).parent.resolve(), path)
        dirPath = p.parent
        if not dirPath.is_dir():
            dirPath.mkdir(parents=True)
        self.filehandler = logging.handlers.TimedRotatingFileHandler(
            str(p),
            when = rotateWen,
            interval = 1,
            backupCount = lotateCount,
            encoding = encoding)
        self.name = name
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        self.filehandler.setFormatter(formatter)

    def getLogger(self, level):
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(level)
        self.logger.addHandler(self.filehandler)

    def debug(self, msg):
        self.getLogger(logging.DEBUG)
        self.logger.debug(msg)

    def info(self, msg):
        self.getLogger(logging.INFO)
        self.logger.info(msg)

    def warning(self, msg):
        self.getLogger(logging.WARNING)
        self.logger.warning(msg)

    def error(self, msg):
        self.getLogger(logging.ERROR)
        self.logger.error(msg)

    def critical(self, msg):
        self.getLogger(logging.CRITICAL)
        self.logger.critical(msg)

    def traceback(self):
        t, v, tb = sys.exc_info()
        f = io.StringIO()
        traceback.print_tb(tb, file=f)
        msg = "type: %s value: %s\ntraceback: %s" % (t, v, f.getvalue())
        self.error(msg)
        print('ERROR Traceback: ' + msg, file=sys.stderr)
