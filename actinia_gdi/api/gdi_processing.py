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

Code based on actinia_core: github.com/mundialis/actinia_core

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


Extension of actinia_cores ephemeral_processing_with_export AsyncEphemeralExportResource to include process chain templates
"""

__license__ = "Apache-2.0"
__author__ = "Anika Bettge, Sören Gebbert"
__copyright__ = "Copyright 2016-2019, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


import pickle
import time
from flask import jsonify, make_response

from copy import deepcopy
from flask_restful_swagger_2 import swagger

from actinia_core.resources.resource_base import ResourceBase
from actinia_core.resources.common.redis_interface import enqueue_job
from actinia_core.resources.ephemeral_processing_with_export import start_job as start_job_ephemeral_processing_with_export, SCHEMA_DOC as SCHEMA_DOC_EPHEMERAL_PROCESSING_WITH_EXPORT
from actinia_core.resources.persistent_processing import start_job as start_job_persistent_processing, SCHEMA_DOC as SCHEMA_DOC_PERSISTENT_PROCESSING
from actinia_core.resources.common.response_models import create_response_from_model

from actinia_gdi.core.gmodulesActinia import createProcessChainTemplateList
from actinia_gdi.core.gmodulesActinia import fillTemplateFromProcessChain
from actinia_gdi.core.gmodulesGrass import createModuleList


def log_error_to_resource_logger(self, msg, rdc):
    """ Logs error which occurs during translation of actinia-module to process
    chain. This case is not handled by EphemeralProcessing from actinia-core as
    _send_resource_error method is used if the error occurs during processing.
    Here a process (g.search.modules) by createModuleList was already processed
    and the actual process chain was not passed to actinia-core, so the error
    occurs before processing.
    """

    data = create_response_from_model(
        user_id=self.user_id,
        resource_id=self.resource_id,
        status="error",
        orig_time=self.orig_time,
        orig_datetime=self.orig_datetime,
        message=msg,
        http_code=400,
        status_url=self.status_url,
        api_info=self.api_info
    )
    self.resource_logger.commit(
        user_id=self.user_id,
        resource_id=self.resource_id,
        document=data,
        expiration=rdc.config.REDIS_RESOURCE_EXPIRE_TIME
    )


def set_actinia_modules(self, rdc, pc_list, grass_module_list, actinia_module_list):
    new_pc = []
    for module in pc_list:
        if "module" in module:
            name = module["module"]
            if name in ["importer", "exporter"]:
                new_pc.append(module)
            elif name in grass_module_list:
                new_pc.append(module)
            elif name in actinia_module_list:
                module_pc = fillTemplateFromProcessChain(module)
                if isinstance(module_pc, str):
                    # then return value is a missing attribute
                    msg = ("Required parameter '%s' missing in actinia-module "
                           " '%s'." % (module_pc, name))
                    log_error_to_resource_logger(self, msg, rdc)
                    return
                elif module_pc is None:
                    msg = "Invalid request for %s" % (name)
                    log_error_to_resource_logger(self, msg, rdc)
                    return
                else:
                    ac_module_pc = set_actinia_modules(self, rdc, module_pc, grass_module_list, actinia_module_list)
                    new_pc.extend(ac_module_pc)
            else:
                msg = ("Module %s is not of type importer, exporter, "
                       "grass-module or an actinia-module." % name)
                log_error_to_resource_logger(self, msg, rdc)
                return
        else:
            new_pc.append(module)
    return new_pc


def preprocess_build_pc_and_enqueue(self, preprocess_kwargs, start_job):
    """ This method looks up the lists of GRASS GIS and actinia modules to
    parse the incoming process chain. If an actinia-module is found, it is
    translated to a process chain via the stored template. The process chain is
    then passed to actinia-core.
    """

    # get grass and actinia module lists
    module_list = createModuleList(self)
    pc_list = createProcessChainTemplateList()
    grass_module_list = []
    actinia_module_list = []

    for module in module_list:
        grass_module_list.append(module['id'])

    for module in pc_list:
        actinia_module_list.append(module['id'])

    # run preprocess again after createModuleList
    rdc = self.preprocess(**preprocess_kwargs)

    if rdc:
        rdc.set_storage_model_to_file()

        new_pc = set_actinia_modules(self, rdc, rdc.request_data['list'], grass_module_list, actinia_module_list)
        rdc.request_data['list'] = new_pc

        enqueue_job(self.job_timeout, start_job, rdc)


class GdiAsyncEphemeralExportResource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a temporary mapset and exports the computed results as geotiff files.
    """

    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc(deepcopy(SCHEMA_DOC_EPHEMERAL_PROCESSING_WITH_EXPORT))
    def post(self, location_name):
        """Execute a user defined process chain in an ephemeral location/mapset
        and store the processing results for download.
        """

        preprocess_kwargs = {}
        preprocess_kwargs['has_json'] = True
        preprocess_kwargs['location_name'] = location_name

        start_job = start_job_ephemeral_processing_with_export

        preprocess_build_pc_and_enqueue(self, preprocess_kwargs, start_job)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class GdiAsyncPersistentResource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a persistent mapset.
    """

    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc(deepcopy(SCHEMA_DOC_PERSISTENT_PROCESSING))
    def post(self, location_name, mapset_name):
        """Execute a user defined process chain that creates a new mapset or
        runs in an existing one.
        """

        preprocess_kwargs = {}
        preprocess_kwargs['has_json'] = True
        preprocess_kwargs['location_name'] = location_name
        preprocess_kwargs['mapset_name'] = mapset_name

        start_job = start_job_persistent_processing

        preprocess_build_pc_and_enqueue(self, preprocess_kwargs, start_job)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)
