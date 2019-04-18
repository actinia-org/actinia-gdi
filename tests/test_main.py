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
from pkg_resources import get_distribution, DistributionNotFound
from flask import Response

import actinia_gdi
from actinia_gdi.main import app


class AppTest(unittest.TestCase):

    def test_app_running(self):
        # from http://flask.pocoo.org/docs/0.12/api/#flask.Flask.test_client:
        # Note that if you are testing for assertions or exceptions in your
        # application code, you must set app.testing = True in order for the
        # exceptions to propagate to the test client.  Otherwise, the exception
        # will be handled by the application (not visible to the test client)
        # and the only indication of an AssertionError or other exception will
        # be a 500 status code response to the test client.

        app.testing = True
        self.app = app.test_client()

        resp = self.app.get('/')
        assert type(resp) is Response

    def test_app_responding(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.get('/')

        assert resp.status_code == respStatusCode

    def test_app_static(self):
        app.testing = True
        self.app = app.test_client()

        respStatusCode = 200

        resp = self.app.get('/index.html')

        assert resp.status_code == respStatusCode


class initTest(unittest.TestCase):

    def test_init(self):
        # TODO: apply to __init__.py
        pkg_version = get_distribution('actinia_gdi.wsgi').version
        assert actinia_gdi.__version__ == pkg_version

        with pytest.raises(DistributionNotFound):
            v = get_distribution('false_distro_name').version
            assert v == 'unknown'


class swaggerTest(unittest.TestCase):

    def test_swagger(self):
        app.testing = True
        self.app = app.test_client()

        resp = self.app.get('/latest/api/swagger.json')
        respData = json.loads(resp.get_data(as_text=True))

        assert type(resp) is Response
        assert type(respData) == dict
        assert respData["info"]["title"] == 'actinia GDI'
