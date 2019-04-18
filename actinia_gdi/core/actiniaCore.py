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


Module to communicate with actinia_core
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import json

import requests
from flask import make_response

from actinia_gdi.resources.config import ACTINIACORE
from actinia_gdi.resources.logging import log
from actinia_gdi.core.common import auth
from actinia_gdi.core.pcBuilder import buildPCDummy
from actinia_gdi.core.pcBuilder import buildPCS1Grd


PROCESSING_ENDPOINT = 'locations/utm32n/processing_async_export'


def parseActiniaIdFromUrl(url):
    id = url.split("/")[-1]
    return id


def parseActiniaAsyncStatusResponse(resp, key):
    """ Method to parse any actinia_core response.

    Args:
    resp: (requests.models.Response): response object
    key: (string): key to return. If not root node, use notation like "a.b.c"

    Returns:
    result: (dict, string, ...): Value of requested key
    """

    keyLen = len(key.split('.'))
    allKeys = key.split('.')

    result = resp

    for i in range(keyLen):
        result = result[allKeys[i]]

    return result


def shortenActiniaCoreResp(fullResp):
    try:
        status = parseActiniaAsyncStatusResponse(fullResp, "status")
        message = parseActiniaAsyncStatusResponse(fullResp, "message")
        url = parseActiniaAsyncStatusResponse(fullResp, "urls.status")
    except Exception:
        return None

    log.info('Status is "' + status + " - " + message + '"')
    return json.loads('{"status": "' + url + '"}')


def postActiniaCore(process, preProcessChain):
    """ Method to start new job in actinia-core

    Args:
    process: (str): the process which is triggered
    preProcessChain: (dict): the enriched preProcessChain object

    Returns:
    TODO: (dict): status url of actinia-core job
    """

    url = ACTINIACORE.url + PROCESSING_ENDPOINT
    headers = {'content-type': 'application/json; charset=utf-8'}

    if process == 'test':
        postbody = buildPCDummy(preProcessChain)
    elif process == 'sentinel1':
        postbody = buildPCS1Grd(preProcessChain)
    else:
        postbody = buildPCDummy(preProcessChain)

    try:
        # TODO: for now if error above, here an empty postbody is send to
        # actinia-core. This leads to correct status "ERROR" at the moment.
        # Make smarter (not call actinia-core, return correct error msg)
        log.info('Posting to ' + url)
        actiniaResp = requests.post(
            url,
            data=postbody,
            headers=headers,
            auth=auth(ACTINIACORE)
        )

        # TODO: remove GET request here. It is a workaround for a bug in
        # actinia-core which does not start a job if no request follows
        actiniaCoreId = json.loads(actiniaResp.text)['resource_id']
        url = ACTINIACORE.url + "resources/actinia-gdi/" + actiniaCoreId
        actiniaResp2 = requests.get(url, auth=auth(ACTINIACORE))

    except requests.exceptions.ConnectionError:
        return None

    return json.loads(actiniaResp2.text)


def cancelActiniaCore(resourceId):
    """ Wrapper method to cancel a job by using the jobId

    This method is called by HTTP POST
    @app.route('/processes/test/jobs/<jobid>/operations/cancel')
    This method is calling core method readJob

    Args:
    resourceId: (string): actinia-core job id

    """
    if resourceId is None:
        return make_response("Not found", 404)

    print("\n Received HTTP DELETE request for job with actinia-core jobID "
          + resourceId)

    DELETING_ENDPOINT = 'resources/'
    url = (ACTINIACORE.url + DELETING_ENDPOINT + ACTINIACORE.user + '/'
           + resourceId)
    log.info('Requesting from ' + url)

    try:
        actiniaResp = requests.delete(url, auth=auth(ACTINIACORE))
    except requests.exceptions.ConnectionError:
        return None
    try:
        status = parseActiniaAsyncStatusResponse(
            json.loads(actiniaResp.text),
            "status"
        )
        message = parseActiniaAsyncStatusResponse(
            json.loads(actiniaResp.text),
            "message"
        )
    except Exception:
        return None

    log.info('Status is "' + status + " - " + message + '"')
    return True
