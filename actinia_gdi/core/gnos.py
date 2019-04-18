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
import xmltodict

from actinia_gdi.core.common import auth
from actinia_gdi.model.geodata import GeodataMeta
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

    url = GEONETWORK.csw_url
    tpl = tplEnv.get_template('geonetwork/post_records_by_tags.xml')
    tags = tags.split(',')
    postbody = tpl.render(tags=tags).replace('\n', '')
    headers = {'content-type': 'application/xml; charset=utf-8'}

    try:
        gnosresp = requests.post(
            url,
            data=postbody,
            headers=headers,
            auth=auth(GEONETWORK)
        )
    except requests.exceptions.ConnectionError:
        return None

    try:
        parsedresp = xmltodict.parse(gnosresp.content)
        records = json.dumps(parsedresp)
        return records
    except Exception:
        return None


def getRecordsByCategory(category):
    """ Method to get records by category from geonetwork

    This method can be called by
    @app.route('/metadata/raw/categories/<category>')
    """

    url = (GEONETWORK.csw_url + '-' + category)
    tpl = tplEnv.get_template('geonetwork/get_records_by_category_kvp.json')
    kvps = json.loads(tpl.render())

    try:
        gnosresp = requests.get(url, params=kvps, auth=auth(GEONETWORK))
    except requests.exceptions.ConnectionError:
        return None

    try:
        parsedresp = xmltodict.parse(gnosresp.content)
        records = json.dumps(parsedresp)
        return records
    except Exception:
        return None


def getRecordByUUID(uuid):
    """ Method to get record by uuid from geonetwork

    This method can be called by @app.route('/metadata/raw/uuids/<uuid>')
    """

    url = GEONETWORK.csw_url
    tpl = tplEnv.get_template('geonetwork/get_record_by_uuid_kvp.json')
    kvps = json.loads(tpl.render(uuid=uuid))

    try:
        gnosresp = requests.get(url, params=kvps, auth=auth(GEONETWORK))
    except requests.exceptions.ConnectionError:
        return None

    try:
        parsedresp = xmltodict.parse(gnosresp.content)
        records = json.dumps(parsedresp)
        return records
    except Exception:
        return None


def parseMeta(record):
    """ Method to parse record from geonetwork with model

    TODO: support more than one tag in response
    TODO: better error handling when attribute not found

    This method can handle GetRecordByIdResponse and GetRecordsResponse
    """

    if 'csw:GetRecordByIdResponse' in record:
        log.info("Found 1 record")
        if 'csw:Record' in json.loads(record)["csw:GetRecordByIdResponse"]:
            recordRoot = (
                json.loads(record)["csw:GetRecordByIdResponse"]["csw:Record"]
            )
        else:
            log.info("...But record is empty")
            return
    elif 'csw:GetRecordsResponse' in record:
        if 'csw:SearchResults' in json.loads(record)["csw:GetRecordsResponse"]:
            searchResults = (
                json.loads(record)["csw:GetRecordsResponse"]["csw:SearchResults"]
            )

        else:
            log.info("...But record is empty")
            return

        numberOfRecords = int(searchResults["@numberOfRecordsReturned"])
        recordRoot = dict()

        if numberOfRecords == 0:
            log.warning("No records found")
            return
        elif numberOfRecords == 1:
            log.info("Found 1 record")
            recordRoot = searchResults["csw:Record"]
        else:
            log.info("Found " + str(numberOfRecords) + " records")
            recordRoot = searchResults["csw:Record"][0]
    else:
        print("Could not parse GNOS response")
        return

    if 'dc:identifier' in recordRoot:
        uuid = recordRoot["dc:identifier"]
    else:
        uuid = 'null'

    if 'ows:BoundingBox' in recordRoot:
        recordBbox = recordRoot["ows:BoundingBox"]

        if 'ows:LowerCorner' in recordBbox:
            bbox_lower = recordBbox["ows:LowerCorner"]

        if 'ows:UpperCorner' in recordBbox:
            bbox_upper = recordBbox["ows:UpperCorner"]

        bbox_a = float(bbox_lower.split(" ")[0])
        bbox_b = float(bbox_lower.split(" ")[1])
        bbox_c = float(bbox_upper.split(" ")[0])
        bbox_d = float(bbox_upper.split(" ")[1])
        bbox = [bbox_a, bbox_b, bbox_c, bbox_d]

        if '@crs' in recordBbox:
            crs = recordBbox["@crs"]
    else:
        bbox = []
        crs = 'null'

    if 'dc:URI' in recordRoot:
        recordUri = recordRoot["dc:URI"]
        if type(recordUri) is dict:
            if "#text" in recordUri:
                table = recordUri["#text"]
        else:
            table = recordUri[0]["#text"]
    else:
        table = 'null'

    geodata_meta = GeodataMeta(
        uuid=uuid,
        bbox=bbox,
        crs=crs,
        table=table
    )

    return geodata_meta


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
