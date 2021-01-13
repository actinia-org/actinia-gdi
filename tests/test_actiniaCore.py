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

__author__ = "Carmen Tawalika and Anika Bettge"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import pytest
import unittest
import json
from flask import Response

from actinia_gdi.main import app

from actinia_gdi.core.actiniaCore import postActiniaCore, cancelActiniaCore
from actinia_gdi.core.jobtable import getJobById


class ActiniaCoreApiTest(unittest.TestCase):

    def test_Connection_get(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.get('/processes/test/connection')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode

    def test_Connection_post(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.post('/processes/test/connection')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode

    def test_getActiniaCore(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.get('/processes/test/jobs')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode


    def test_postActiniaCore(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        with open('tests/resources/postbody.processes.success.json') as jsonfile:
            postBody = json.load(jsonfile)

        resp = self.app.post('/processes/test/jobs',
                             data=json.dumps(postBody),
                             content_type='application/json')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode

    def test_postActiniaCoreFailure(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 500

        with open('tests/resources/postbody.processes.failure.json') as jsonfile:
            postBody = json.load(jsonfile)

        resp = self.app.post('/processes/test/jobs',
                             data=json.dumps(postBody),
                             content_type='application/json')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode


class ActiniaCoreCoreTest(unittest.TestCase):
    def test_postActiniaCore(self):

        with open('tests/resources/postbody.processes.success.json') as jsonfile:
            jsonDict = json.load(jsonfile)

        process = postActiniaCore('test', jsonDict, 'http://127.0.0.1:5000')

        assert type(process) == dict

    def test_cancelActiniaCore(self):

        jobid = 1
        job = getJobById(jobid)
        resourceId = job['actinia_core_jobid']
        resp = cancelActiniaCore(resourceId)

        assert resp
