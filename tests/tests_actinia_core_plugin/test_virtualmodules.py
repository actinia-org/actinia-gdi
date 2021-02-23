#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 mundialis GmbH & Co. KG

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Test Module Lists and Self-Description
"""

__license__ = "Apache-2.0"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2021, mundialis"


from flask import Response

from actinia_core.resources.common.app import URL_PREFIX

from testsuite import ActiniaTestCase, compare_module_to_file

GrassModules = ['r.slope.aspect', 'importer', 'exporter']
someActiniaModules = [
    'add_enumeration', 'default_value', 'nested_modules_test',
    'point_in_polygon', 'slope_aspect', 'vector_area', 'index_NDVI']
someVirtualModules = GrassModules + someActiniaModules


class VirtualModulesTest(ActiniaTestCase):

    def test_list_virtual_modules_get(self):
        global someVirtualModules

        respStatusCode = 200
        resp = self.app.get(URL_PREFIX + '/modules',
                            headers=self.user_auth_header)

        assert type(resp) is Response
        assert resp.status_code == respStatusCode
        assert hasattr(resp, 'json')
        assert 'grass-module' in resp.json['processes'][0]['categories']
        assert 'actinia-module' in resp.json['processes'][-1]['categories']

        assert len(resp.json['processes']) > 500
        assert 'categories' in resp.json['processes'][0]
        assert 'description' in resp.json['processes'][0]
        assert 'id' in resp.json['processes'][0]

        respModules = [i['id'] for i in resp.json['processes']]

        for i in someVirtualModules:
            assert i in respModules


for i in someVirtualModules:
    # create method for every actinia-module to have a better overview in
    # test summary
    def_name = "test_describe_virtual_module_get_" + i
    compare_module_to_file.__defaults__ = ('modules', i,)
    setattr(VirtualModulesTest, def_name, compare_module_to_file)
