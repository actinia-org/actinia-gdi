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


Test
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import pytest
import unittest
import json
from flask import Response
import requests

from actinia_gdi.main import app

from actinia_gdi.core.gnosReader import getRecordsByCategory
from actinia_gdi.core.gnosReader import getRecordByUUID, getRecordsByTags
from actinia_gdi.core.gnosReader import getMetaByUUID, getMetaByTags
from actinia_gdi.core.gnosParser import parseMeta
from actinia_gdi.model.regeldatei import GeodataMeta


class GnosApiTest(unittest.TestCase):

    def test_Connection_get(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200
        # respData = '{"status": "success"}'

        resp = self.app.get('/metadata/test/connection')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode
        # assert resp.get_data(as_text=True) == respData

    def test_Connection_post(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.post('/metadata/test/connection')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode

    def test_RawTag(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.get('/metadata/raw/tags/Eurasia')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode

    def test_RawCategory(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.get('/metadata/raw/categories/mfg')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode

    def test_RawUuid(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        testUuid = 'da165110-88fd-11da-a88f-000d939bc5d8'

        resp = self.app.get('/metadata/raw/uuids/' + testUuid)

        assert type(resp) is Response
        assert resp.status_code == respStatusCode

    def test_Tag(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.get('/metadata/geodata/tags/Eurasia')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode

    def test_Uuid(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.get('/metadata/geodata/uuids/da165110-88fd-11da-a88f-000d939bc5d8')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode


class GnosCoreTest(unittest.TestCase):

    # def test_checkConnection(self):
    #     assert checkConnection() is True
    #
    #     with pytest.raises(requests.exceptions.ConnectionError):
    #         checkConnection()
    #     assert checkConnection() is False

    def test_getRecordsByTags(self):
        records = getRecordsByTags('Eurasia')
        recordsAsDict = json.loads(records)

        assert type(records) == str
        assert type(recordsAsDict) == dict
        assert type(recordsAsDict["csw:GetRecordsResponse"]) == dict

    def test_getRecordsByCategory(self):
        records = getRecordsByCategory('mfg')
        recordsAsDict = json.loads(records)

        assert type(records) == str
        assert type(recordsAsDict) == dict
        assert type(recordsAsDict["csw:GetRecordsResponse"]) == dict

    def test_getRecordByUUID(self):
        records = getRecordByUUID('da165110-88fd-11da-a88f-000d939bc5d8')
        recordsAsDict = json.loads(records)

        assert type(records) == str
        assert type(recordsAsDict) == dict
        assert type(recordsAsDict["csw:GetRecordByIdResponse"]) == dict

    def test_getMetaByUUID(self):
        geodata_meta = getMetaByUUID('da165110-88fd-11da-a88f-000d939bc5d8')
        assert type(geodata_meta) == GeodataMeta

    def test_getMetaByTags_1(self):
        geodata_meta = getMetaByTags('Eurasia')  # 1
        assert type(geodata_meta) == GeodataMeta

    def test_getMetaByTags_2(self):
        geodata_meta = getMetaByTags('*')  # 2
        assert type(geodata_meta) == GeodataMeta

    def test_getMetaByTags_0(self):
        geodata_meta = getMetaByTags('eura')  # 0
        assert geodata_meta is None

    def test_parseMeta(self):
        error = parseMeta("false")
        assert error is None
