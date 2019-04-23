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


Module for shared methods
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import json

import requests
import xmltodict
from requests.auth import HTTPBasicAuth

from actinia_gdi.resources.logging import log


def auth(CONFIG):
    """ Method to create HTTPBasicAuth from config credentials
    """
    user = CONFIG.user
    password = CONFIG.password

    auth = HTTPBasicAuth(user, password)

    return auth


def checkConnection(url, name, expectedFormat):
    """ Method to test connection

    Args:
      url (string): url of resource to test.
      name (string): name of resource to test. Only used for logging
      expectedFormat (string): Format in which resource will respond. Can be
        'xml' or 'json'
    """

    # can be called by e.g.
    # checkConnection(GEONETWORK.csw_url, 'geonetwork', 'xml')

    log.debug('Testing connection to ' + url)

    try:
        resp = requests.get(url)
    except requests.exceptions.ConnectionError:
        log.error('Connection Error to ' + name)
        return None

    try:
        if expectedFormat == 'xml':
            parsedresp = xmltodict.parse(resp.content)
            records = json.dumps(parsedresp)
        elif expectedFormat == 'json':
            parsedresp = json.loads(resp.text)

        log.debug('Connection successfull to ' + name)
        return True

    except Exception:
        log.error('Connection Error to ' + name)
        return None


def start_job(timeout, func, *args):
    """Execute the provided function in a subprocess
    Args:
        func: The function to call from the subprocess
        *args: The function arguments
    Returns:
    """
    # Just starting the process
    from multiprocessing import Process
    p = Process(target=func, args=args)
    p.start()

    return
