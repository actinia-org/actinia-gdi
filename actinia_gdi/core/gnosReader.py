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


Module to read from geonetwork
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import json

import requests

from actinia_gdi.core.common import auth
from actinia_gdi.core.gnosParser import parseMeta
from actinia_gdi.resources.config import GEONETWORK
from actinia_gdi.resources.logging import log
from actinia_gdi.resources.templating import tplEnv


def getRecordsByTags(tags):
    """ Method to get records by tags from geonetwork

    Attention: The tags received are case sensitive!
    PropertyIsLike is sensitive, matchCase not possible here.
    See https://trac.osgeo.org/geonetwork/wiki/CSW202Improvements

    This method can be called by @app.route('/metadata/raw/tags/<tags>')
    """

    log.debug('looking for tags ' + str(tags))

    try:
        url = GEONETWORK.csw_url
        tpl = tplEnv.get_template('geonetwork/post_records_by_tags.xml')
        tags = tags.split(',')
        postbody = tpl.render(tags=tags).replace('\n', '')
        headers = {'content-type': 'application/xml; charset=utf-8'}
    except Exception as e:
        log.error('Could not set needed variable')
        log.error(e)
        return None

    try:
        gnosresp = requests.post(
            url,
            data=postbody,
            headers=headers,
            auth=auth(GEONETWORK)
        )
        return gnosresp.content
    except requests.exceptions.ConnectionError:
        log.error('Could not connect to gnos')
        return None


def getRecordsByCategory(category):
    """ Method to get records by category from geonetwork

    This method can be called by
    @app.route('/metadata/raw/categories/<category>')
    """

    try:
        url = (GEONETWORK.csw_url + '-' + category)
        tpl = tplEnv.get_template('geonetwork/get_records_by_category_kvp.json')
        kvps = json.loads(tpl.render())
    except Exception as e:
        log.error('Could not set needed variable')
        log.error(e)
        return None

    try:
        gnosresp = requests.get(url, params=kvps, auth=auth(GEONETWORK))
        return gnosresp.content
    except requests.exceptions.ConnectionError:
        log.error('Could not connect to gnos')
        return None


def getRecordByUUID(uuid):
    """ Method to get record by uuid from geonetwork

    This method can be called by @app.route('/metadata/raw/uuids/<uuid>')
    """

    try:
        url = GEONETWORK.csw_url
        tpl = tplEnv.get_template('geonetwork/get_record_by_uuid_kvp.json')
        kvps = json.loads(tpl.render(uuid=uuid))
    except Exception as e:
        log.error('Could not set needed variable')
        log.error(e)
        return None

    try:
        gnosresp = requests.get(url, params=kvps, auth=auth(GEONETWORK))
        return gnosresp.content
    except requests.exceptions.ConnectionError:
        log.error('Could not connect to gnos')
        return None


def getMetaByUUID(uuid):
    """ Method to get parsed record by uuid from geonetwork

    This method can be called by @app.route('/metadata/geodata/uuids/<uuid>')
    """

    record = getRecordByUUID(uuid)

    if record is not None:
        geodata_meta = parseMeta(record)
        return geodata_meta
    else:
        error = "could not get record for uuid from gnos"
        print(error)
        return None


def getMetaByTags(tags):
    """ Method to get parsed records by tags from geonetwork

    TODO: add BBOX in request
    TODO: support more than first tag in response

    This method can be called by @app.route('/metadata/geodata/tags/<tags>')
    """

    if type(tags) is str:
        tag = tags
    else:
        tag = tags[0]

    record = getRecordsByTags(tag)

    if record is not None:
        geodata_meta = parseMeta(record)
        return geodata_meta
    else:
        error = "could not get record for tags from gnos"
        print(error)
        return None
