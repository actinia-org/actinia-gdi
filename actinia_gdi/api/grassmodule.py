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

"""
import json
import os
import pickle
import shutil
import uuid

from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
from flask_restful_swagger_2 import Schema

from actinia_core.resources.resource_base import ResourceBase

from actinia_gdi.apidocs import grassmodule
from actinia_gdi.core.common import start_job
from actinia_gdi.core.grassmodule import initGrass, deinitGrass
from actinia_gdi.core.grassmodule import EphemeralModuleLister
from actinia_gdi.core.grassmodule import ParseInterfaceDescription
from actinia_gdi.model.grassmodule import Module, ModuleList

__license__ = "GPLv3"
__author__ = "Anika Bettge, Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Anika Bettge, Carmen Tawalika"


class ListModules(ResourceBase):
    """List all modules
    """
    layer_type = None

    @swagger.doc(grassmodule.listModules_get_docs)
    def get(self):
        """Get a list of all modules.
        """

        location_name = initGrass(self)

        # self.user_credentials["permissions"]['accessible_datasets'][location_name] = ['PERMANENT']

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name="PERMANENT")

        process_chain = {"1": {"module": "g.search.modules",
                               "inputs": {"keyword": ""},
                               "flags": "j"}}

        def list_modules(*args, process_chain=process_chain):
            processing = EphemeralModuleLister(*args, pc=process_chain)
            processing.run()

        if rdc:
            start_job(self.job_timeout, list_modules, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        j_data = json.loads(response_model['process_log'][-1]['stdout'])

        module_list = []
        for data in j_data:
            description = data['attributes']['description']
            keywords = data['attributes']['keywords']
            name = data['name']
            categories = (keywords.split(','))
            categories.append("grass-module")
            module_response = (Module(id=name, description=description, categories=sorted(categories)))
            module_list.append(module_response)

        deinitGrass(self, location_name)

        return make_response(jsonify(ModuleList(status="success", processes=module_list)), 200)


class DescribeModule(ResourceBase):
    """ Definition for endpoint @app.route('modules/<module>') to
        desctibe one module

    Contains HTTP GET endpoint
    Contains swagger documentation
    """
    @swagger.doc(grassmodule.describeModule_get_docs)
    def get(self, module):

        location_name = initGrass(self)

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name="PERMANENT")

        process_chain = {"1": {"module": module,
                               "interface-description": "True"}}

        def describe_module(*args, process_chain=process_chain):
            processing = EphemeralModuleLister(*args, pc=process_chain)
            processing.run()

        if rdc:
            start_job(self.job_timeout, describe_module, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        xml_string = response_model['process_log'][0]['stdout']

        grass_module = ParseInterfaceDescription(xml_string)

        deinitGrass(self, location_name)

        return make_response(jsonify(grass_module), 200)
