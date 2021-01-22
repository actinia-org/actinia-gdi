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


Module management

* List all modules
* Describe single module
"""

__license__ = "Apache-2.0"
__author__ = "Anika Bettge, Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Anika Bettge, Carmen Tawalika"


from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
from actinia_core.resources.resource_base import ResourceBase

from actinia_gdi.apidocs import gmodules
from actinia_gdi.core.gmodulesGrass import createModuleList, createGrassModule
from actinia_gdi.model.gmodules import ModuleList
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel


class ListModules(ResourceBase):
    """List all GRASS modules
    """

    @swagger.doc(gmodules.listModules_get_docs)
    def get(self):
        """Get a list of all GRASS GIS modules.
        """

        module_list = createModuleList(self)

        return make_response(jsonify(ModuleList(
            status="success",
            processes=module_list)), 200)


class DescribeModule(ResourceBase):
    """ Definition for endpoint @app.route('grassmodules/<grassmodule>') to
        desctibe one module

    Contains HTTP GET endpoint
    Contains swagger documentation
    """
    @swagger.doc(gmodules.describeGrassModule_get_docs)
    def get(self, grassmodule):
        """Describe a GRASS GIS module.
        """

        try:
            grass_module = createGrassModule(self, grassmodule)
            return make_response(jsonify(grass_module), 200)
        except Exception:
            res = (jsonify(SimpleStatusCodeResponseModel(
                status=404,
                message='Error looking for module "' + grassmodule + '".'
            )))
            return make_response(res, 404)
