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


Module management to parser GRASS xml response
"""

__license__ = "Apache-2.0"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Carmen Tawalika"


import json
import xmltodict

from actinia_gdi.model.gmodules import Module
from actinia_gdi.model.gmodules import ModuleParameter, ModuleParameterSchema
from actinia_gdi.resources.logging import log
from actinia_gdi.resources.templating import tplEnv


def logstring(module_id, param, key):
    log.debug(module_id + " " + param + " has no key " + key)
    pass


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
        param_descr = parameter['label'] + ". "
        kwargs['description'] = param_descr
    except KeyError:
        # logstring(module_id, key, "label")
        pass
    try:
        param_descr += parameter['description'] + ". "
        kwargs['description'] = param_descr
    except KeyError:
        logstring(module_id, key, "description")

    return kwargs


def setParameterName(key, kwargs):
    kwargs['name'] = key
    return kwargs


def setParameterOptional(parameter, kwargs):
    try:
        required = parameter['@required']
        if required == 'yes':
            kwargs['optional'] = False
        else:
            kwargs['optional'] = True
    except KeyError:
        required = "False"

    return kwargs


def setParameterDefault(parameter, kwargs):
    try:
        kwargs['default'] = parameter['default']
        if parameter['default'] is None:
            kwargs['default'] = ''
    except KeyError:
        pass

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


def createModuleParameterFromGrassParam(module_id, key, parameter):
    kwargs = dict()
    schema_kwargs = dict()

    schema_kwargs = setParamType(module_id, key, parameter, schema_kwargs)
    kwargs = setParameterDescription(module_id, key, parameter, kwargs)
    kwargs = setParameterName(key, kwargs)
    kwargs = setParameterOptional(parameter, kwargs)
    kwargs = setParameterDefault(parameter, kwargs)
    schema_kwargs = setParameterEnum(parameter, schema_kwargs)

    param_object = ModuleParameter(
        **kwargs,
        schema=ModuleParameterSchema(**schema_kwargs)
    )

    del kwargs
    del schema_kwargs

    return param_object


def createModuleParameterFromGrassFlag(module_id, key, parameter):

    kwargs = dict()
    kwargs['default'] = 'False'
    schema_kwargs = dict()
    schema_kwargs['type'] = 'boolean'

    key = setParameterKey(module_id, parameter)

    kwargs = setParameterDescription(module_id, key, parameter, kwargs)
    kwargs = setParameterName(key, kwargs)
    kwargs = setParameterOptional(parameter, kwargs)

    param_object = ModuleParameter(
        **kwargs,
        schema=ModuleParameterSchema(**schema_kwargs)
    )
    del kwargs
    del schema_kwargs

    return param_object


def ParseInterfaceDescription(xml_string, keys=None):
    """Parses output of GRASS interface-description
    and returns openEO process object
    """

    gm_dict = xmltodict.parse(xml_string)['task']

    module_id = gm_dict['@name']
    description = gm_dict['description']
    categories = gm_dict['keywords'].replace(' ', '').split(',')
    categories.append('grass-module')
    parameters = []
    returns = []
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
        if keys:
            # case for actinia modules
            key = setVirtualParameterKey(module_id, parameter)
            key_exists = False
            if key not in keys:
                for actiniakey in keys:
                    if actiniakey.startswith(key):
                        key_exists = True
            else:
                key_exists = True
            if not key_exists:
                continue
        else:
            # case for GRASS modules
            key = setParameterKey(module_id, parameter)
        param_object = createModuleParameterFromGrassParam(
            module_id, key, parameter)
        if isOutput(parameter):
            returns.append(param_object)
        else:
            parameters.append(param_object)

    for parameter in flags:
        # not possible to specify flag values via template at the moment
        if keys:
            continue
        param_object = createModuleParameterFromGrassFlag(
            module_id, key, parameter)

        parameters.append(param_object)

    # custom extention for importer + exporter from actinia_core
    # Runs when viewing importer/exporter as module and when used in template.
    try:
        tpl = tplEnv.get_template('gmodules/' + module_id + '.json')
        pc_template = json.loads(tpl.render().replace('\n', ''))
        for key in [*pc_template]:
            extrakwargs[key] = []
            for param in pc_template[key]:
                extrakwargs[key].append(ModuleParameter(**param))
    except Exception as e:
        # if no template for module exist, use as is (default)
        # log.debug('template %s does not exist.', e)
        pass

    grass_module = Module(
        id=module_id,
        description=description,
        categories=sorted(categories),
        parameters=parameters,
        returns=returns,
        **extrakwargs
    )

    return grass_module
