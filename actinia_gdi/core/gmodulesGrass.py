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
Module management related to GRASS modules

"""
import json
import time

from actinia_core.resources.common.response_models import create_response_from_model

from actinia_gdi.core.gmodulesProcessor import run_process_chain
from actinia_gdi.core.gmodulesParser import ParseInterfaceDescription
from actinia_gdi.model.gmodules import Module


__license__ = "GPLv3"
__author__ = "Anika Bettge, Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Anika Bettge, Carmen Tawalika"


def createModuleList(self):

    process_chain = {"1": {"module": "g.search.modules",
                           "inputs": {"keyword": ""},
                           "flags": "j"}}

    response = run_process_chain(self, process_chain)

    j_data = json.loads(response['process_log'][-1]['stdout'])

    # overwrite previous entries commited by EphemeralModuleLister in case the
    # further processing fails (e.g. invalid json). Else, the resource exists
    # and shows the output of g.search.modules.
    data = create_response_from_model(
        user_id=self.user_id,
        resource_id=self.resource_id,
        status='',
        orig_time=time.time(),
        orig_datetime='',
        message=''
    )
    self.resource_logger.commit(user_id=self.user_id, resource_id=self.resource_id, document=data,expiration=1)

    module_list = []
    for data in j_data:
        description = data['attributes']['description']
        keywords = data['attributes']['keywords']
        name = data['name']
        categories = (keywords.split(','))
        categories.append("grass-module")
        module_response = (Module(
            id=name,
            description=description,
            categories=sorted(categories)
        ))
        module_list.append(module_response)

    return module_list


def createGrassModule(self, module):
    process_chain = {"1": {"module": module,
                           "interface-description": True}}
    response = run_process_chain(self, process_chain)

    xml_string = response['process_log'][0]['stdout']
    grass_module = ParseInterfaceDescription(xml_string)

    return grass_module
