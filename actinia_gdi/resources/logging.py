#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2018-present mundialis GmbH & Co. KG

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


The logger
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import logging
from datetime import datetime
from logging import FileHandler

from colorlog import ColoredFormatter
from pythonjsonlogger import jsonlogger
from werkzeug.serving import WSGIRequestHandler

from actinia_gdi.resources.config import LOGCONFIG


# TODO: Notice: do not call logging.warning (will create new logger for ever)
# logging.warning("called actinia_gdi logger after 1")


log = logging.getLogger('actinia-gdi')
werkzeugLog = logging.getLogger('werkzeug')


def setLogFormat(veto=None):
    logformat = ""
    if LOGCONFIG.type == 'json' and not veto:
        logformat = CustomJsonFormatter('(time) (level) (component) (module)'
                                        '(message) (pathname) (lineno)'
                                        '(processName) (threadName)')
    else:
        logformat = ColoredFormatter(
            '%(log_color)s[%(asctime)s] %(levelname)-10s: %(name)s.%(module)-'
            '10s -%(message)s [in %(pathname)s:%(lineno)d]%(reset)s'
        )
    return logformat


def setWerkzeugFormat():
    werkzeugLogformat = ""
    if LOGCONFIG.type == 'json':
        werkzeugLogformat = CustomJsonFormatter('(time) (level) (component) '
                                                '(message) (processName) '
                                                '(threadName)')
    else:
        werkzeugLogformat = ColoredFormatter(
            '%(log_color)s[%(asctime)s] %(levelname)-10s: %(name)-22s -'
            '%(message)s %(reset)s'
        )
    return werkzeugLogformat


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # (Pdb) dir(record)
        # ... 'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName'
        # ,'getMessage', 'levelname', 'levelno', 'lineno', 'message', 'module',
        # 'msecs', 'msg', 'name', 'pathname', 'process', 'processName',
        # 'relativeCreated', 'stack_info', 'thread', 'threadName']

        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['time'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

        log_record['component'] = record.name


def createLogger():
    # create logger, set level and define format
    log.setLevel(getattr(logging, LOGCONFIG.level))
    fileformat = setLogFormat('veto')
    stdoutformat = setLogFormat()

    # Setup the logger handler for stdout
    handler = logging.StreamHandler()
    handler.setFormatter(stdoutformat)
    log.addHandler(handler)

    # Setup the logger handler for filesystem. If json, it still is not json
    # for readability
    file_handler = FileHandler(LOGCONFIG.logfile)
    file_handler.setFormatter(fileformat)
    log.addHandler(file_handler)


def createWerkzeugLogger():
    werkzeugLog.setLevel(getattr(logging, LOGCONFIG.level))
    werkzeugLogformat = setWerkzeugFormat()

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


createLogger()
createWerkzeugLogger()
