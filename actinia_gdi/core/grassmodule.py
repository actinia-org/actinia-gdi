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
import os
import shutil
import uuid
import xmltodict

from actinia_core.resources.common.config import global_config
from actinia_core.resources.ephemeral_processing import EphemeralProcessing
from actinia_core.resources.common.response_models import \
    StringListProcessingResultResponseModel, \
    ProcessingErrorResponseModel

from actinia_gdi.model.grassmodule import Module
from actinia_gdi.model.grassmodule import ModuleParameter, ModuleParameterSchema
from actinia_gdi.resources.logging import log


__license__ = "GPLv3"
__author__ = "Anika Bettge"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Anika Bettge"


def initGrass(self):
        """
        * not using enqueue_job to get always a response
        * the function creates a new location cause not all users can access
          a location
        """

        # check if location exists
        location_name = 'location_for_listing_modules_' + str(uuid.uuid4())
        location = os.path.join(global_config.GRASS_DATABASE, location_name) # '/actinia_core/grassdb/location_for_listing_modules'
        # Check the location path
        if os.path.isdir(location):
            return self.get_error_response(message="Unable to create location. "
                                                   "Location <%s> exists in global database." % location_name)
        # Check also for the user database
        location = os.path.join(self.grass_user_data_base, self.user_group, location_name) # '/actinia_core/userdata/superadmin/location_for_listing_modules'
        # Check the location path
        if os.path.isdir(location):
            return self.get_error_response(message="Unable to create location. "
                                                   "Location <%s> exists in user database." % location_name)

        # create new location cause not each user can access a location
        if not os.path.isdir(os.path.join(self.grass_user_data_base, self.user_group)):
            os.mkdir(os.path.join(self.grass_user_data_base, self.user_group))
        os.mkdir(location)
        mapset = os.path.join(location, 'PERMANENT')
        os.mkdir(mapset)
        with open(os.path.join(mapset, 'DEFAULT_WIND'), 'w') as out:
            out.write("proj:       3\nzone:       0\nnorth:      1N\n"
                + "south:      0\neast:       1E\nwest:       0\ncols:       1"
                + "\nrows:       1\ne-w resol:  1\nn-s resol:  1\ntop:        "
                + "1.000000000000000\nbottom:     0.000000000000000\ncols3:   "
                + "   1\nrows3:      1\ndepths:     1\ne-w resol3: 1\nn-s reso"
                + "l3: 1\nt-b resol:  1")
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
            out.write("proj:       3\nzone:       0\nnorth:      1N\n"
                + "south:      0\neast:       1E\nwest:       0\ncols:       1"
                + "\nrows:       1\ne-w resol:  1\nn-s resol:  1\ntop:        "
                + "1.000000000000000\nbottom:     0.000000000000000\ncols3:   "
                + "   1\nrows3:      1\ndepths:     1\ne-w resol3: 1\nn-s reso"
                + "l3: 1\nt-b resol:  1")

        return location_name

def deinitGrass(self, location_name):
        """
        * the function deletes above location
        """
        # remove location
        location = os.path.join(global_config.GRASS_DATABASE, location_name)
        if os.path.isdir(location):
            shutil.rmtree(location)
        location = os.path.join(self.grass_user_data_base, self.user_group, location_name)
        if os.path.isdir(location):
            shutil.rmtree(location)
        # del self.user_credentials["permissions"]['accessible_datasets'][location_name]


class EphemeralModuleLister(EphemeralProcessing):
    """List all modules
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


def logstring(module_id, param, key):
    log.debug(module_id + " " + param + " has no key " + key)


def setParameterKey(module_id, parameter):
    try:
        key = parameter['@name']
    except KeyError:
        key = None
        logstring(module_id, key, "name")

    return key


def setParameterDescription(module_id, key, parameter, kwargs):
    param_descr = ""

    try:
        param_descr = parameter['label']
        kwargs['description'] = param_descr
    except KeyError:
        # logstring(module_id, key, "label")
        pass
    try:
        param_descr += '. ' + parameter['description']
        kwargs['description'] = param_descr
    except KeyError:
        logstring(module_id, key, "description")

    return kwargs


def setParameterRequired(parameter, kwargs):
    try:
        required = parameter['@required']
        if required == 'yes':
            kwargs['required'] = True
        else:
            kwargs['required'] = False
    except KeyError:
        required = "False"

    return kwargs


def setParamType(module_id, key, parameter, schema_kwargs):
    try:
        # grass parameter types can only be string, double or integer
        gtype = parameter['@type']
        if gtype == 'float' or gtype == 'double':
            gtype = 'number'
        schema_kwargs['type'] = gtype
    except KeyError:
        logstring(module_id, key, "type")
    try:
        multiple = parameter['@multiple']
        if multiple == 'yes':
            gtype = 'array'
        schema_kwargs['type'] = gtype
    except KeyError:
        logstring(module_id, key, "multiple")
    try:
        for subtype_key, val in parameter['gisprompt'].items():
            if subtype_key == "@element":
                schema_kwargs['subtype'] = val
    except Exception:
        pass

    return schema_kwargs


def setParameterDefault(parameter, schema_kwargs):
    try:
        schema_kwargs['default'] = parameter['default']
        if parameter['default'] is None:
            schema_kwargs['default'] = ''
    except KeyError:
        pass

    return schema_kwargs


def setParameterEnum(parameter, schema_kwargs):
    try:
        enum = []
        for enum_key, val in parameter['values'].items():
            for item in val:
                for i in item:
                    if i == "name":
                        enum.append(item[i])
        if len(enum) > 0:
            schema_kwargs['enum'] = enum
    except KeyError:
        pass

    return schema_kwargs


def ParseInterfaceDescription(xml_string):
    """Parses output of GRASS interface-description
    and returns openEO process object
    """

    gm_dict = xmltodict.parse(xml_string)['task']

    module_id = gm_dict['@name']
    description = gm_dict['description']
    categories = gm_dict['keywords'].replace(' ', '').split(',')
    categories.append('grass-module')
    parameters = {}

    try:
        grass_params = gm_dict['parameter']
    except KeyError:
        logstring(module_id, "", "has no parameter")
        grass_params = []

    try:
        flags = gm_dict['flag']
    except KeyError:
        logstring(module_id, "", "has no flags")
        flags = []

    for parameter in grass_params:
        kwargs = dict()
        schema_kwargs = dict()

        key = setParameterKey(module_id, parameter)

        schema_kwargs = setParamType(module_id, key, parameter, schema_kwargs)
        kwargs = setParameterDescription(module_id, key, parameter, kwargs)
        kwargs = setParameterRequired(parameter, kwargs)
        schema_kwargs = setParameterDefault(parameter, schema_kwargs)
        schema_kwargs = setParameterEnum(parameter, schema_kwargs)

        param_object = ModuleParameter(
            **kwargs,
            schema=ModuleParameterSchema(**schema_kwargs)
        )
        parameters[key] = param_object
        del kwargs
        del schema_kwargs

    for parameter in flags:
        kwargs = dict()
        schema_kwargs = dict()
        schema_kwargs['type'] = 'boolean'
        schema_kwargs['default'] = 'False'

        key = setParameterKey(module_id, parameter)

        kwargs = setParameterDescription(module_id, key, parameter, kwargs)
        kwargs = setParameterRequired(parameter, kwargs)

        param_object = ModuleParameter(
            **kwargs,
            schema=ModuleParameterSchema(**schema_kwargs)
        )
        parameters[key] = param_object
        del kwargs
        del schema_kwargs

    grass_module = Module(
        id=module_id,
        description=description,
        categories=sorted(categories),
        parameters=parameters
    )

    return grass_module
