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
CRUD
* Create process chains template
* Read process chain template
* Update process chain template
* Delete process chain template
* List all process chains templates
"""

__license__ = "Apache-2.0"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2021, mundialis"
__maintainer__ = "Carmen Tawalika"


from flask import jsonify, make_response, request
from actinia_core.resources.resource_base import ResourceBase

from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel
from actinia_gdi.core.actinia_module import readAllActiniaModules
from actinia_gdi.core.actinia_module import createActiniaModule
from actinia_gdi.core.actinia_module import readActiniaModule
from actinia_gdi.core.actinia_module import updateActiniaModule
from actinia_gdi.core.actinia_module import deleteActiniaModule


class ActiniaModule(ResourceBase):
    """List all actinia modules (process chain templates)
    """

    # @swagger.doc(TODO)
    def get(self):
        """Get a list of all actinia modules (process chain templates).
        """
        actinia_module_list = readAllActiniaModules()
        return make_response(jsonify(actinia_module_list), 201)

    # @swagger.doc(TODO)
    def post(self):
        """Create an actinia module (process chain template).
        """
        actinia_module = createActiniaModule(request.get_json(force=True))
        return make_response(jsonify(actinia_module), 201)


class ActiniaModuleId(ResourceBase):
    """ Manage actinia modules (process chain templates)
    """

    # @swagger.doc(TODO)
    def get(self, module_id):
        """Describe an actinia module (process chain templat).
        """
        actinia_module = readActiniaModule(module_id)
        if actinia_module is not False:
            return make_response(jsonify(actinia_module), 201)
        else:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error'
                   )))
            return make_response(res, 404)

    # @swagger.doc(TODO)
    def put(self, module_id):
        """Update an actinia module (process chain templat).
        """
        actinia_module = updateActiniaModule(
            module_id, request.get_json(force=True))
        if actinia_module is not False:
            return make_response(jsonify(actinia_module), 201)
        else:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error'
                   )))
            return make_response(res, 404)

    # @swagger.doc(TODO)
    def delete(self, module_id):
        """Delete an actinia module (process chain templat).
        """
        resp = deleteActiniaModule(module_id)
        if resp is True:
            return make_response(jsonify(resp), 201)
        else:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error'
                   )))
            return make_response(res, 404)
