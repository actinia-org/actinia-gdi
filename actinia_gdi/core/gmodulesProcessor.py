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


Module management to run GRASS tasks
"""

__license__ = "Apache-2.0"
__author__ = "Anika Bettge"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Anika Bettge"


import os
import shutil
import pickle
import uuid

from actinia_core.resources.common.config import global_config
from actinia_core.resources.ephemeral_processing import EphemeralProcessing
from actinia_core.resources.common.response_models import \
    StringListProcessingResultResponseModel, \
    ProcessingErrorResponseModel

from actinia_gdi.core.common import start_job


def initGrass(self):
    """
    * not using enqueue_job to get always a response
    * the function creates a new location cause not all users can access
    a location
    """

    # check if location exists
    location_name = 'location_for_listing_modules_' + str(uuid.uuid4())
    # '/actinia_core/grassdb/location_for_listing_modules'
    location = os.path.join(global_config.GRASS_DATABASE, location_name)
    # Check the location path
    if os.path.isdir(location):
        msg = ("Unable to create location. "
               "Location <%s> exists in global database." % location_name)
        return self.get_error_response(message=msg)
    # Check also for the user database
    # '/actinia_core/userdata/superadmin/location_for_listing_modules'
    location = os.path.join(
        self.grass_user_data_base,
        self.user_group, location_name
    )
    # Check the location path
    if os.path.isdir(location):
        msg = ("Unable to create location. "
               "Location <%s> exists in user database." % location_name)
        return self.get_error_response(message=msg)

    # create new location cause not each user can access a location
    if not os.path.isdir(
        os.path.join(self.grass_user_data_base, self.user_group)
    ):
        os.mkdir(os.path.join(self.grass_user_data_base, self.user_group))
    os.mkdir(location)
    mapset = os.path.join(location, 'PERMANENT')
    os.mkdir(mapset)
    with open(os.path.join(mapset, 'DEFAULT_WIND'), 'w') as out:
        wind = ("proj:       3\nzone:       0\nnorth:      1N\n"
                + "south:      0\neast:       1E\nwest:       0\ncols:       1"
                + "\nrows:       1\ne-w resol:  1\nn-s resol:  1\ntop:        "
                + "1.000000000000000\nbottom:     0.000000000000000\ncols3:   "
                + "   1\nrows3:      1\ndepths:     1\ne-w resol3: 1\nn-s reso"
                + "l3: 1\nt-b resol:  1")
        out.write(wind)
    with open(os.path.join(mapset, 'MYNAME'), 'w') as out:
        out.write("")
    with open(os.path.join(mapset, 'PROJ_EPSG'), 'w') as out:
        out.write("epsg: 4326")
    with open(os.path.join(mapset, 'PROJ_INFO'), 'w') as out:
        out.write("name: WGS 84\ndatum: wgs84\nellps: wgs84\nproj: ll\n"
                  + "no_defs: defined\ntowgs84: 0.000,0.000,0.000")
    with open(os.path.join(mapset, 'PROJ_UNITS'), 'w') as out:
        out.write("unit: degree\nunits: degrees\nmeters: 1.0")
    with open(os.path.join(mapset, 'WIND'), 'w') as out:
        wind = ("proj:       3\nzone:       0\nnorth:      1N\n"
                + "south:      0\neast:       1E\nwest:       0\ncols:       1"
                + "\nrows:       1\ne-w resol:  1\nn-s resol:  1\ntop:        "
                + "1.000000000000000\nbottom:     0.000000000000000\ncols3:   "
                + "   1\nrows3:      1\ndepths:     1\ne-w resol3: 1\nn-s reso"
                + "l3: 1\nt-b resol:  1")
        out.write(wind)

    return location_name


def deinitGrass(self, location_name):
    """
    * the function deletes above location
    """
    # remove location
    location = os.path.join(global_config.GRASS_DATABASE, location_name)
    if os.path.isdir(location):
        shutil.rmtree(location)
    location = os.path.join(
        self.grass_user_data_base,
        self.user_group, location_name
    )
    if os.path.isdir(location):
        shutil.rmtree(location)
    # del self.user_credentials["permissions"]['accessible_datasets'][location_name]


class EphemeralModuleLister(EphemeralProcessing):
    """ Overwrites EphemeralProcessing from actinia_core to bypass permission
    check for modules and temporary location, needed for self-description
    """

    def __init__(self, *args, pc):
        EphemeralProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel
        self.process_chain = pc

    def _execute(self, skip_permission_check=True):

        self._setup()

        # Create the temporary database and link all available mapsets into is
        self._create_temp_database()

        process_list = self._validate_process_chain(
            process_chain=self.process_chain,
            skip_permission_check=True
        )

        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name="PERMANENT"
        )

        self._execute_process_list(process_list)

        self.module_results = self.module_output_log[0]["stdout"]


def run_process_chain(self, process_chain):
    """ Used to list all GRASS modules, to describe a certain GRASS module
    and to generate actinia module description out of containing GRASS modules.
    ATTENTION! This call skips permission checks, so temporary location can be used. If user is not allowed to use GRASS modules used here, this will be
    allowed in these cases.
    """

    location_name = initGrass(self)

    # self.user_credentials["permissions"]['accessible_datasets'][location_name] = ['PERMANENT']

    rdc = self.preprocess(has_json=False, has_xml=False,
                          location_name=location_name,
                          mapset_name="PERMANENT")

    def list_modules(*args, process_chain=process_chain):
        processing = EphemeralModuleLister(*args, pc=process_chain)
        processing.run()

    if rdc:
        start_job(self.job_timeout, list_modules, rdc)
        http_code, response_model = self.wait_until_finish()
    else:
        http_code, response_model = pickle.loads(self.response_data)

    deinitGrass(self, location_name)

    return response_model
