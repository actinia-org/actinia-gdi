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
Process chain template management
For now we only support read. In the future we want a whole CRUD.
For now the templates are stored file based.

* List all process chains templates
* Describe single process chain template

"""
from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
from flask_restful import Resource
from actinia_core.resources.resource_base import ResourceBase

from actinia_gdi.apidocs import gmodules
from actinia_gdi.core.gmodulesActinia import createProcessChainTemplateList
from actinia_gdi.core.gmodulesActinia import createActiniaModule
from actinia_gdi.model.gmodules import ModuleList
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel


__license__ = "GPLv3"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Carmen Tawalika"


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

    @swagger.doc(gmodules.describeModule_get_docs)
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
