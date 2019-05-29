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
Module management related to process chain templates

"""
import json
from jinja2 import meta

from actinia_gdi.core.gmodulesProcessor import run_process_chain
from actinia_gdi.core.gmodulesParser import ParseInterfaceDescription
from actinia_gdi.model.gmodules import Module
from actinia_gdi.resources.templating import pcTplEnv


__license__ = "GPLv3"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Carmen Tawalika"


def filter_func(name):
    ''' filter examples out of template folder
    '''

    if "example" not in name:
        return True
    return False


def renderTemplate(pc):

    # find variables from processchain and render template with variables
    tpl_source = pcTplEnv.loader.get_source(pcTplEnv, pc + '.json')[0]
    parsed_content = pcTplEnv.parse(tpl_source)
    # {'column_name', 'name'}
    undef = meta.find_undeclared_variables(parsed_content)

    kwargs = {}
    for i in undef:
        kwargs[i] = '{{ ' + i + ' }}'

    tpl = pcTplEnv.get_template(pc + '.json')
    pc_template = json.loads(tpl.render(**kwargs).replace('\n', ''))

    return pc_template


def createProcessChainTemplateList():

    pc_list = []
    tpl_list = pcTplEnv.list_templates(filter_func=filter_func)

    for tpl_string in tpl_list:
        tpl = pcTplEnv.get_template(tpl_string)
        pc_template = json.loads(tpl.render().replace('\n', ''))

        tpl_id = pc_template['id']
        description = pc_template['description']
        categories = ['actinia-module']

        pc_response = (Module(
            id=tpl_id,
            description=description,
            categories=categories
        ))
        pc_list.append(pc_response)

    return pc_list


def createActiniaModule(self, processchain):
    '''
       processchain is the name of the template that is requested
       exec_process_chain is the pc that is created to request module
       descriptions from within GRASS via actinia
    '''

    pc_template = renderTemplate(processchain)
    processes = pc_template['template']['list']

    count = 1
    exec_process_chain = dict()
    aggregated_keys = []
    aggregated_vals = []

    for i in processes:

        # create the exec_process_chain item
        module = i['module']
        item_key = str(count)
        pc_item = {item_key: {"module": module,
                              "interface-description": True}}
        exec_process_chain.update(pc_item)
        count = count + 1

        # aggregate all keys where values are a variable
        # in the processchain template
        # only aggregate them if the template value differs
        inputs = i['inputs']
        for j in inputs:
            val = j['value']
            key = module + '_' + j['param']
            if '{{ ' in val and ' }}' in val and val not in aggregated_vals:
                aggregated_vals.append(val)
                aggregated_keys.append(key)

    response = run_process_chain(self, exec_process_chain)
    xml_strings = response['process_log']

    grass_module_list = []
    virtual_module_params = {}

    for i in xml_strings:
        xml_string = i['stdout']
        grass_module = ParseInterfaceDescription(
            xml_string,
            keys=aggregated_keys
        )
        grass_module_list.append(grass_module)
        for param in grass_module['parameters']:
            virtual_module_params[param] = grass_module['parameters'][param]

    virtual_module = Module(
        id=pc_template['id'],
        description=pc_template['description'],
        categories=['actinia-module'],
        parameters=virtual_module_params
    )

    return virtual_module
