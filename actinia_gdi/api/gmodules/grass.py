# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#######

"""
Module management


* List all modules
* Describe single module

"""
from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
from actinia_core.resources.resource_base import ResourceBase

from actinia_gdi.apidocs import gmodules
from actinia_gdi.core.gmodulesGrass import createModuleList, createGrassModule
from actinia_gdi.model.gmodules import ModuleList
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel


__license__ = "GPLv3"
__author__ = "Anika Bettge, Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Anika Bettge, Carmen Tawalika"


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
    @swagger.doc(gmodules.describeModule_get_docs)
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
