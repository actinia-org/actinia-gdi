# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2019-present Sören Gebbert and mundialis GmbH & Co. KG
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
Extension of actinia_cores ephemeral_processing_with_export AsyncEphemeralExportResource to include process chain templates
"""
import pickle
from flask import jsonify, make_response

from copy import deepcopy
from flask_restful_swagger_2 import swagger
from actinia_core.resources.resource_base import ResourceBase
from actinia_core.resources.common.redis_interface import enqueue_job
from actinia_core.resources.common.response_models import SimpleResponseModel
from actinia_core.resources.ephemeral_processing_with_export import EphemeralProcessingWithExport, start_job, SCHEMA_DOC

from actinia_gdi.core.gmodulesActinia import createProcessChainTemplateList
from actinia_gdi.core.gmodulesActinia import fillTemplateFromProcessChain
from actinia_gdi.core.gmodulesGrass import createModuleList


__license__ = "GPLv3"
__author__ = "Anika Bettge, Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"


class GdiAsyncEphemeralExportResource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a temporary mapset and exports the computed results as geotiff files.
    """
    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):
        """Execute a user defined process chain in an ephemeral location/mapset and store the processing results
        for download.
        """
        # get grass and actinia module lists
        module_list = createModuleList(self)
        pc_list = createProcessChainTemplateList()
        # TODO: find out size before ?
        grass_module_list = []
        actinia_module_list = []

        for module in module_list:
            grass_module_list.append(module['id'])

        for module in pc_list:
            actinia_module_list.append(module['id'])

        rdc = self.preprocess(has_json=True, location_name=location_name)

        if rdc:
            rdc.set_storage_model_to_file()

            new_pc = []
            for module in rdc.request_data['list']:
                if "module" in module:
                    name = module["module"]
                    if name == "importer" or name == "exporter":
                        new_pc.append(module)
                    elif name in grass_module_list:
                        new_pc.append(module)
                    elif name in actinia_module_list:
                        module_pc = fillTemplateFromProcessChain(module)
                        if isinstance(module_pc, str):
                            # then return value is a missing attribute
                            msg = "Required parameter '%s' missing in Module '%s'." % (module_pc, name)
                            return make_response(jsonify(SimpleResponseModel(
                                status="error",
                                message=msg
                            )), 400)
                        elif module_pc is None:
                            msg = "Invalid request for %s" % (name)
                            return make_response(jsonify(SimpleResponseModel(
                                status="error",
                                message=msg
                            )), 400)
                        else:
                            new_pc.extend(module_pc)
                    else:
                        msg = "Module %s is not of type importer, exporter, grass-module or an actinia-module." % name
                        return make_response(jsonify(SimpleResponseModel(
                            status="error",
                            message=msg
                        )), 400)
                else:
                    new_pc.append(module)

            rdc.request_data['list'] = new_pc

            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)
