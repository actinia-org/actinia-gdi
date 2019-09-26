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
Module management and Process chain template management

* List all modules + List all process chains templates
* Describe single module + Describe single process chain template

"""
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


__license__ = "GPLv3"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Carmen Tawalika"


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
