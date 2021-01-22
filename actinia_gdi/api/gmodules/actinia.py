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


Process chain template management
For now we only support read. In the future we want a whole CRUD.
For now the templates are stored file based.

* List all process chains templates
* Describe single process chain template
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
from actinia_gdi.model.gmodules import ModuleList
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel


class ListProcessChainTemplates(Resource):
    """List all process chain templates
    """

    @swagger.doc(gmodules.listModules_get_docs)
    def get(self):
        """Get a list of all actinia modules (process chain templates).
        """

        pc_list = createProcessChainTemplateList()

        return make_response(jsonify(
            ModuleList(status="success", processes=pc_list)), 200)


class DescribeProcessChainTemplate(ResourceBase):
    """ Describe process chain template as "virtual GRASS module"

    Contains HTTP GET endpoint
    Contains swagger documentation
    """

    @swagger.doc(gmodules.describeActiniaModule_get_docs)
    def get(self, actiniamodule):
        """Describe an actinia module (process chain template).
        """

        try:
            virtual_module = createActiniaModule(self, actiniamodule)
            return make_response(jsonify(virtual_module), 200)
        except Exception:
            msg = 'Error looking for actinia module "' + actiniamodule + '".'
            res = (jsonify(SimpleStatusCodeResponseModel(status=404, message=msg)))
            return make_response(res, 404)
