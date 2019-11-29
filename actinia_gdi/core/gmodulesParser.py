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
Module management to parser GRASS xml response

"""
import json
import xmltodict

from actinia_gdi.model.gmodules import Module
from actinia_gdi.model.gmodules import ModuleParameter, ModuleParameterSchema
from actinia_gdi.resources.logging import log
from actinia_gdi.resources.templating import tplEnv


__license__ = "GPLv3"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Carmen Tawalika"


def logstring(module_id, param, key):
    log.debug(module_id + " " + param + " has no key " + key)


def setParameterKey(module_id, parameter):
    try:
        key = parameter['@name']
    except KeyError:
        key = None
        logstring(module_id, key, "name")

    return key


def setVirtualParameterKey(module_id, parameter):
    try:
        key = module_id + '_' + parameter['@name']
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
        if gtype in ('float', 'double'):
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


def isOutput(parameter):
    """ Checks if parameter is output parameter.
    Returns True if parameter has key
    'gisprompt.age' == 'new',
    False otherwise.
    """
    try:
        if '@age' in parameter['gisprompt'].keys():
            return (parameter['gisprompt']['@age'] == 'new')
        else:
            return False
    except KeyError:
        return False


def ParseInterfaceDescription(xml_string, keys=None):
    """Parses output of GRASS interface-description
    and returns openEO process object
    """

    gm_dict = xmltodict.parse(xml_string)['task']

    module_id = gm_dict['@name']
    description = gm_dict['description']
    categories = gm_dict['keywords'].replace(' ', '').split(',')
    categories.append('grass-module')
    parameters = {}
    returns = {}
    extrakwargs = dict()

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

        if keys:
            # case for actinia modules
            key = setVirtualParameterKey(module_id, parameter)
            if key not in keys:
                continue
        else:
            # case for GRASS modules
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
        if isOutput(parameter):
            returns[key] = param_object
        else:
            parameters[key] = param_object
        del kwargs
        del schema_kwargs

    for parameter in flags:
        # not possible to specify flag values via template at the moment
        if keys:
            continue

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

    # custom extention for importer + exporter from actinia_core
    try:
        tpl = tplEnv.get_template('gmodules/' + module_id + '.json')
        pc_template = json.loads(tpl.render().replace('\n', ''))
        for key in [*pc_template]:
            extrakwargs[key] = {}
            for param in pc_template[key]:
                extrakwargs[key][param] = ModuleParameter(**pc_template[key][param])
    except Exception as e:
        # if no template for module exist, use as is (default)
        log.debug('template %s does not exist.', e)

    grass_module = Module(
        id=module_id,
        description=description,
        categories=sorted(categories),
        parameters=parameters,
        returns=returns,
        **extrakwargs
    )

    return grass_module
