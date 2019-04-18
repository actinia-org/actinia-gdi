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


import unittest
import json
from flask import Response

from actinia_gdi.main import app


class ApiTest(unittest.TestCase):

    def test_GetResources(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 405

        resp = self.app.get('/resources/processes/operations/update')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode

    def test_PostResources(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        # TODO: example actinia-core-response is gone!
        with open('tests/resources/actinia-core-resp.json') as jsonfile:
            postBody = json.load(jsonfile)

        resp = self.app.post('/resources/processes/operations/update',
                             data=str(json.dumps(postBody)),
                             content_type='application/json')

        assert type(resp) is Response
        assert resp.status_code == respStatusCode
