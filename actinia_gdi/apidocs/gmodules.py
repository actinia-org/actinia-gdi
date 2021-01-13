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


Documentation objects for GRASS modules and process chain template
api endpoints
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import copy

from actinia_core.resources.common.response_models import ProcessingErrorResponseModel

from actinia_gdi.model.gmodules import Module, ModuleList


null = "null"


listModules_get_docs = {
    'tags': ['Module Management'],
    'description': 'Get a list of modules. '
                   'Minimum required user role: user.',
    'responses': {
        '200': {
            'description': 'This response returns a list of module names and the log '
                           'of the process chain that was used to create the response.',
            'schema': ModuleList
        },
        '400': {
            'description': 'The error message and a detailed log why listing of '
                           'modules did not succeeded',
            'schema': ProcessingErrorResponseModel
        }
    }
}
Module = {}
ProcessingErrorResponseModel = {}

describeModule_get_docs = {
    'tags': ['Module Management'],
    "parameters": [
        {
            "in": "path",
            "name": "module",
            "type": "string",
            "description": "The name of a module",
            "required": True
        }
    ],
    'description': 'Get the description of a module. '
                   'Minimum required user role: user.',
    'responses': {
        '200': {
            'description': 'This response returns a description of a module.',
            'schema': Module
        },
        '400': {
            'description': 'The error message and a detailed log why '
                           'describing modules did not succeeded',
            'schema': ProcessingErrorResponseModel
        }
    }
}


describeActiniaModule_get_docs = copy.deepcopy(describeModule_get_docs)
describeActiniaModule_get_docs['parameters'][0]['name'] = "actiniamodule"

describeGrassModule_get_docs = copy.deepcopy(describeModule_get_docs)
describeGrassModule_get_docs['parameters'][0]['name'] = "grassmodule"
