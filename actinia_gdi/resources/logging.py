import logging
from logging import FileHandler

from colorlog import ColoredFormatter
from werkzeug.serving import WSGIRequestHandler

from actinia_gdi.resources.config import LOGCONFIG


# TODO: Notice: do not call logging.warning (will create new logger for ever)
# logging.warning("called actinia_gdi logger after 1")


log = logging.getLogger('actinia-gdi')
werkzeugLog = logging.getLogger('werkzeug')


def createLogger():
    # create logger, set level and define format
    log.setLevel(getattr(logging, LOGCONFIG.level))
    logformat = ColoredFormatter(
        '%(log_color)s[%(asctime)s] %(levelname)-10s: %(name)s.%(module)-10s -'
      '%(message)s [in %(pathname)s:%(lineno)d]%(reset)s'
    )

    # Setup the logger handler for stdout
    handler = logging.StreamHandler()
    handler.setFormatter(logformat)
    log.addHandler(handler)

    # Setup the logger handler for filesystem
    file_handler = FileHandler(LOGCONFIG.logfile)
    file_handler.setFormatter(logformat)
    log.addHandler(file_handler)


def createWerkzeugLogger():
    werkzeugLog.setLevel(getattr(logging, LOGCONFIG.level))
    werkzeugLogformat = ColoredFormatter(
        '%(log_color)s[%(asctime)s] %(levelname)-10s: %(name)-22s -'
      '%(message)s %(reset)s'
    )

    # Setup the logger handler for stdout
    werkzeugHandler = logging.StreamHandler()
    werkzeugHandler.setFormatter(werkzeugLogformat)
    werkzeugLog.addHandler(werkzeugHandler)

    # Setup the logger handler for filesystem
    werkzeugFile_handler = FileHandler(LOGCONFIG.logfile)
    werkzeugFile_handler.setFormatter(werkzeugLogformat)
    werkzeugLog.addHandler(werkzeugFile_handler)


class MyRequestHandler(WSGIRequestHandler):

    def log(self, type, message, *args):
        getattr(werkzeugLog, type)(
            self.address_string() + ": " + (message % args)
        )


# TODO: delete line if not needed
# logging.root.setLevel(getattr(logging, LOGCONFIG.level))

createLogger()
createWerkzeugLogger()
