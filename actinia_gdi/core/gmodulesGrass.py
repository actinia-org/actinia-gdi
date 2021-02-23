#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2018-2021 mundialis GmbH & Co. KG

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Module management related to GRASS modules
"""

__license__ = "Apache-2.0"
__author__ = "Anika Bettge, Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Anika Bettge, Carmen Tawalika"


import json
import time

from actinia_core.resources.common.response_models import create_response_from_model

from actinia_gdi.core.gmodulesProcessor import run_process_chain
from actinia_gdi.core.gmodulesParser import ParseInterfaceDescription
from actinia_gdi.model.gmodules import Module


def createModuleList(self):

    process_chain = {"1": {"module": "g.search.modules",
                           "inputs": {"keyword": ""},
                           "flags": "j"}}

    response = run_process_chain(self, process_chain)

    j_data = json.loads(response['process_log'][-1]['stdout'])

    # overwrite previous entries commited by EphemeralModuleLister in case the
    # further processing fails (e.g. invalid json). Else, the resource exists
    # and shows the output of g.search.modules.
    data = create_response_from_model(
        user_id=self.user_id,
        resource_id=self.resource_id,
        status='',
        orig_time=time.time(),
        orig_datetime='',
        message=''
    )
    self.resource_logger.commit(user_id=self.user_id, resource_id=self.resource_id, document=data,expiration=1)

    module_list = []
    for data in j_data:
        description = data['attributes']['description']
        keywords = data['attributes']['keywords']
        name = data['name']
        categories = (keywords.split(','))
        categories.append("grass-module")
        module_response = (Module(
            id=name,
            description=description,
            categories=sorted(categories)
        ))
        module_list.append(module_response)

    return module_list


def createGrassModule(self, module):
    process_chain = {"1": {"module": module,
                           "interface-description": True}}
    response = run_process_chain(self, process_chain)

    xml_string = response['process_log'][0]['stdout']
    grass_module = ParseInterfaceDescription(xml_string)

    return grass_module
