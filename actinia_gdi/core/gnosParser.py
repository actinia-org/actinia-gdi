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


Module to communicate with geonetwork
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import json

import xmltodict
from xml.dom.minidom import parseString

from actinia_gdi.model.geodata import GeodataMeta
from actinia_gdi.resources.logging import log


def makeItJson(xml):
    try:
        parsedresp = xmltodict.parse(xml)
        records = json.dumps(parsedresp)
        return records
    except Exception:
        log.error('Error parsing XML response from gnos')
        return None


def makeItXml(jsonDict):
    try:
        records = xmltodict.unparse(jsonDict)
        return records
    except Exception:
        log.error('Error converting json back to xml')
        return None


def getRecordRoot(record):
    """ Method to get one record out of the geonetwork response. Valid for
    both schemata 'gmd:MD_Metadata' and 'csw:Record'

    TODO: support more than one tag in response

    This method can handle GetRecordByIdResponse and GetRecordsResponse
    """

    record = json.loads(record)

    if 'csw:GetRecordByIdResponse' in record:
        log.info("Found 1 record")

        if 'gmd:MD_Metadata' in record["csw:GetRecordByIdResponse"]:
            recordRoot = (
                record["csw:GetRecordByIdResponse"]["gmd:MD_Metadata"]
            )
        elif 'csw:Record' in record["csw:GetRecordByIdResponse"]:
            recordRoot = (
                record["csw:GetRecordByIdResponse"]["csw:Record"]
            )
        else:
            log.info("...But record is empty")
            return

    elif 'csw:GetRecordsResponse' in record:

        if 'csw:SearchResults' in record["csw:GetRecordsResponse"]:
            searchResults = (
                record["csw:GetRecordsResponse"]["csw:SearchResults"]
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
            recordRoot = searchResults["gmd:MD_Metadata"]
            if not recordRoot:
                recordRoot = searchResults["csw:Record"]
        else:
            log.info("Found " + str(numberOfRecords) + " records")
            recordRoot = searchResults["gmd:MD_Metadata"][0]
            if not recordRoot:
                recordRoot = searchResults["csw:Record"][0]

    else:
        print("Could not parse GNOS response")
        return

    return recordRoot


def getUuidByRecordRoot(recordRoot):

    try:
        uuid = recordRoot["gmd:fileIdentifier"]["gco:CharacterString"]
        if not uuid:
            uuid = recordRoot["dc:identifier"]
    except Exception:
        log.warning('Could not set uuid')
        uuid = 'null'

    return uuid


def getBboxByRecordRoot(recordRoot):

    try:
        recordExtent = (
            recordRoot["gmd:identificationInfo"]
            ["gmd:MD_DataIdentification"]["gmd:extent"]
        )

        def parseExtent(bboxRoot):
            bbox_a = bboxRoot["gmd:eastBoundLongitude"]["gco:Decimal"]
            bbox_b = bboxRoot["gmd:southBoundLatitude"]["gco:Decimal"]
            bbox_c = bboxRoot["gmd:westBoundLongitude"]["gco:Decimal"]
            bbox_d = bboxRoot["gmd:northBoundLatitude"]["gco:Decimal"]
            bbox = [
                float(bbox_a),
                float(bbox_b),
                float(bbox_c),
                float(bbox_d)
            ]
            return bbox

        if type(recordExtent) is list:
            for i in recordExtent:
                if 'gmd:geographicElement' in i["gmd:EX_Extent"]:

                    geoEl = i["gmd:EX_Extent"]["gmd:geographicElement"]

                    if type(geoEl) is list:
                        bbox = []
                        for i in geoEl:
                            if 'gmd:EX_GeographicBoundingBox' in i:
                                bboxRoot = i["gmd:EX_GeographicBoundingBox"]
                                bbox = parseExtent(bboxRoot)

                    else:
                        bboxRoot = geoEl["gmd:EX_GeographicBoundingBox"]
                        bbox = parseExtent(bboxRoot)

        else:
            bbox = []

    except Exception:
        log.warning('Could not set bbox')
        bbox = []

    return bbox


def parseMeta(recordXml):
    """ Method to parse record from geonetwork with schema 'gmd' with model

    This method can handle GetRecordByIdResponse and GetRecordsResponse
    """

    record = makeItJson(recordXml)

    if record is None:
        return None

    recordRoot = getRecordRoot(record)

    uuid = getUuidByRecordRoot(recordRoot)

    bbox = getBboxByRecordRoot(recordRoot)

    try:
        table = (
            recordRoot["gmd:distributionInfo"]["gmd:MD_Distribution"]
            ["gmd:transferOptions"]["gmd:MD_DigitalTransferOptions"]
            ["gmd:onLine"]["gmd:CI_OnlineResource"]["gmd:linkage"]["gmd:URL"]
        )
    except Exception:
        log.warning('Could not set table')
        table = 'null'

    try:
        format = (
            recordRoot["gmd:distributionInfo"]["gmd:MD_Distribution"]
            ["gmd:distributionFormat"]["gmd:MD_Format"]["gmd:name"]
            ["gco:CharacterString"]
        )
    except Exception:
        log.warning('Could not set format')
        format = 'null'

    try:
        featureCatalogUuid = (
            recordRoot["gmd:contentInfo"]["gmd:MD_FeatureCatalogueDescription"]
            ["gmd:featureCatalogueCitation"]["@uuidref"]
        )
    except Exception:
        log.warning('Could not set featureCatalogUuid')
        featureCatalogUuid = 'null'

    try:
        crs = (
            recordRoot['gmd:referenceSystemInfo']['gmd:MD_ReferenceSystem']
            ['gmd:referenceSystemIdentifier']['gmd:RS_Identifier']['gmd:code']
            ['gco:CharacterString']
        )
    except Exception:
        log.warning('Could not set crs')
        crs = 'null'

    # TODO: write parsing function if we need to find id column for processing
    # of materialized views
    try:
        log.warning('Feature Catalog UUID is: ' + featureCatalogUuid)
    #     featRec = getRecordByUUID(featureCatalogUuid)
    #     featRecRoot = json.loads(featRec)['csw:GetRecordByIdResponse']['csw:Record']
    #     featRecAttr = featRecRoot['dc:subject']
    #     for i in featRecAttr:
    #         if 'idpk' in i:
    #             featureCatalogIdColumn = i
    #     log.warning('Feature Catalog ID column is: ' + featureCatalogIdColumn)
    except Exception:
        log.warning('Could not set featureCatalogIdColumn from CatalogUuid')

    geodata_meta = GeodataMeta(
        uuid=uuid,
        bbox=bbox,
        crs=crs,
        table=table,
        format=format
    )

    return geodata_meta


def parseMetaCsw(record):
    """ Method to parse record from geonetwork with standart output schema
    'csw' with model. Not used here, we use gmd schema

    TODO: better error handling when attribute not found

    This method can handle GetRecordByIdResponse and GetRecordsResponse
    """

    recordRoot = getRecordRoot(record)

    uuid = getUuidByRecordRoot(recordRoot)

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

    if 'dc:format' in recordRoot:
        # TODO: find out why it is listed two times and if it can differ
        format = recordRoot["dc:format"][0]
    else:
        format = 'null'

    geodata_meta = GeodataMeta(
        uuid=uuid,
        bbox=bbox,
        crs=crs,
        table=table,
        format=format
    )

    return geodata_meta


def updateXml(response, utcnow):

    try:
        doc = parseString(response.decode('utf-8'))
        recordNode = doc.getElementsByTagName('gmd:MD_Metadata')[0]

        dateStampEl = recordNode.getElementsByTagName('gmd:dateStamp')[0]
        dateEl = dateStampEl.getElementsByTagName('gco:Date')
        if len(dateEl) is 0:
            dateEl = dateStampEl.getElementsByTagName('gco:DateTime')
            if len(dateEl) is 0:
                log.error('Could not find date element')
                return None
            else:
                dateEl = dateEl[0]

        else:
            dateEl = dateEl[0]
            utcnow = utcnow.split('T')[0]

        if dateEl.firstChild.nodeType != dateEl.TEXT_NODE:
            raise Exception("node does not contain text")

        dateEl.firstChild.replaceWholeText(utcnow)

        record = recordNode.toxml().replace('\n', '')

    except Exception as e:
        log.error('Could not set date in metadata record')
        log.error(e)
        return None

    return record
