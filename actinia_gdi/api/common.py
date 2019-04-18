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


Common api methods
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from flask import make_response, jsonify

from actinia_gdi.model.responseModels import SimpleResponseModel
from actinia_gdi.core import common
from actinia_gdi.resources.config import ACTINIACORE
from actinia_gdi.resources.config import GEONETWORK
from actinia_gdi.resources.logging import log


def checkConnection(name):
    """ Method to test connection

    Args:
      name (string): resource to test. Can be 'actinia-core' or 'geonetwork'

    Returns:
      response (Response): of type SimpleResponseModel telling
      connection success or failure
    """

    if name == 'actinia-core':
        url = ACTINIACORE.url + "version"
        name = 'actinia-core'
        type = 'json'
    elif name == 'geonetwork':
        url = GEONETWORK.csw_url
        name = 'geonetwork'
        type = 'xml'

    try:
        records = common.checkConnection(url, name, type)
    except Exception:
        log.error("Don't know which connection to test")

    if records is not None:
        res = jsonify(SimpleResponseModel(status=200, message="success"))
        return make_response(res, 200)
    elif records is None:
        res = jsonify(SimpleResponseModel(status=404, message="failure"))
        return make_response(res, 200)


def checkConnectionWithoutResponse(name):
    """ Method to test connection

    Args:
      name (string): resource to test. Can be 'actinia-core' or 'geonetwork'
    """

    if name == 'actinia-core':
        url = ACTINIACORE.url + "version"
        name = 'actinia-core'
        type = 'json'
    elif name == 'geonetwork':
        url = GEONETWORK.csw_url
        name = 'geonetwork'
        type = 'xml'

    try:
        connectionTest = common.checkConnection(url, name, type)
        return connectionTest
    except Exception:
        log.error("Don't know which connection to test")
        return None
