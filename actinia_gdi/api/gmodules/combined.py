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


Module management and Process chain template management

* List all modules + List all process chains templates
* Describe single module + Describe single process chain template
"""

__license__ = "Apache-2.0"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Carmen Tawalika"


from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
from flask_restful import Resource
from actinia_core.resources.resource_base import ResourceBase

from actinia_gdi.apidocs import gmodules
from actinia_gdi.core.gmodulesActinia import createProcessChainTemplateList
from actinia_gdi.core.gmodulesActinia import createActiniaModule
from actinia_gdi.core.gmodulesGrass import createModuleList, createGrassModule
from actinia_gdi.model.gmodules import ModuleList
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel


class ListVirtualModules(ResourceBase):
    """List all GRASS GIS modules and process chain templates
    """

    @swagger.doc(gmodules.listModules_get_docs)
    def get(self):
        """Get a list of all modules.
        """

        module_list = createModuleList(self)
        pc_list = createProcessChainTemplateList()

        for i in pc_list:
            module_list.append(i)

        return make_response(jsonify(
            ModuleList(status="success", processes=module_list)), 200)


class DescribeVirtualModule(ResourceBase):
    """ Describe module or process chain template

    Contains HTTP GET endpoint
    Contains swagger documentation
    """

    @swagger.doc(gmodules.describeModule_get_docs)
    def get(self, module):
        """Describe a module.
        """

        try:
            try:
                virtual_module = createGrassModule(self, module)
            except Exception:
                virtual_module = createActiniaModule(self, module)
            finally:
                return make_response(jsonify(virtual_module), 200)

        except Exception:
            msg = 'Error looking for module "' + module + '".'
            res = (jsonify(SimpleStatusCodeResponseModel(status=404, message=msg)))
            return make_response(res, 404)
