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
import re

from actinia_gdi.core.gmodulesProcessor import run_process_chain
from actinia_gdi.core.gmodulesParser import ParseInterfaceDescription
from actinia_gdi.model.gmodules import Module
from actinia_gdi.resources.templating import pcTplEnv
from actinia_gdi.resources.logging import log


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
    '''
       list all stored templates and return as actinia-module list
    '''

    pc_list = []
    tpl_list = pcTplEnv.list_templates(filter_func=filter_func)

    for tpl_string in tpl_list:
        tpl = pcTplEnv.get_template(tpl_string)
        try:
            pc_template = json.loads(tpl.render().replace('\n', ''))
        except:
            log.error('Error parsing template ' + tpl_string)

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


def add_param_description(moduleparameter, param, input_dict):

    # update description and mention grass module parameter
    suffix = " [generated from " + param + "]"
    moduleparameter['description'] += suffix
    # add comment if there is one in process chain template

    if param in input_dict and 'comment' in input_dict[param]:
        comment = input_dict[param]['comment']
        moduleparameter['description'] += " - " + comment
        # moduleparameter['comment'] = comment


def createActiniaModule(self, processchain):
    '''
       This method is used to create self-descriptions for actinia-modules.
       In this method the terms "processchain" and "exec_process_chain" are
       used. "processchain" is the name of the template for which the
       description is requested, "exec_process_chain" is the pc that is created
       to collect all module descriptions referenced in the template.

       This method loads a stored process-chain template and for each GRASS
       module that is found, it checks if one value contains a placeholder. If
       this is the case and the name of the placeholder variable was not used by
       another GRASS module already, a new exec_process_chain item is generated,
       requesting the interface description from GRASS GIS. Then the whole
       exec_process_chain with all interface descriptions is executed.
       The response is parsed to show one actinia-module containing only the
       attributes which can be replaced in the processchain template.
    '''

    pc_template = renderTemplate(processchain)
    processes = pc_template['template']['list']

    aggregated_vals = []
    input_dict = {}
    import_descr_dict = {}
    exporter_dict = {}
    count = 1

    for i in processes:

        # create the exec_process_chain item
        module = i['module']
        processid = i['id']
        # TODO: display this in module description?
        # if hasattr(i, 'comment'):
        #     comment = i['comment']

        inOrOutputs = []
        if i.get('inputs') is not None:
            inOrOutputs += i.get('inputs')
        if i.get('outputs') is not None:
            inOrOutputs += i.get('outputs')

        run_interface_descr = False
        input_dict[processid] = {}
        input_dict[processid]["gparams"] = {}

        # aggregate all keys where values are a variable
        # in the processchain template
        # only aggregate them if the template value differs
        for j in inOrOutputs:
            val = j['value']
            key = module + '_' + j['param']
            uuid = processid + '_' + j['param']
            if '{{ ' in val and ' }}' in val and val not in aggregated_vals:
                aggregated_vals.append(val)
                run_interface_descr = True
                input_dict[processid]["gparams"][key] = {}

                # matches placeholder in longer value, e.g. in
                # 'res = if(input <= {{ my_values }}, 1, null() )'
                # beware that in general it is easier to make the whole value
                # a placeholder. Might be not possible for e.g. r.mapcalc
                placeholder = re.search(r"\{\{(.*?)\}\}", str(val)).groups()[0]
                amkey = placeholder.strip(' ')
                input_dict[processid]["gparams"][key]['amkey'] = amkey
                if 'comment' in j:
                    input_dict[processid]["gparams"][key]['comment'] = j['comment']

            if 'import_descr' in j:
                for key, val in j['import_descr'].items():
                    if '{{ ' in val and ' }}' in val:
                        run_interface_descr = True
                        # TODO: check if only part of value can be placeholder
                        stripval = val.strip('{{').strip('}}').strip(' ')
                        import_descr_dict[stripval] = key

            if 'exporter' in j:
                for key, val in j['exporter'].items():
                    if '{{ ' in val and ' }}' in val:
                        run_interface_descr = True
                        # TODO: check if only part of value can be placeholder
                        stripval = val.strip('{{').strip('}}').strip(' ')
                        exporter_dict[stripval] = key

        if run_interface_descr:
            item_key = str(count)
            pc_item = {item_key: {"module": module,
                                  "interface-description": True}}
            response = run_process_chain(self, pc_item)
            xml_strings = response['process_log']
            count = count + 1
            input_dict[processid]['xml_string'] = xml_strings[0]['stdout']
        else:
            del input_dict[processid]

    virtual_module_params = {}
    virtual_module_returns = {}

    for k,v in input_dict.items():
        xml_string = v['xml_string']
        aggregated_keys = v['gparams']
        grass_module = ParseInterfaceDescription(
            xml_string,
            keys=aggregated_keys.keys()
        )

        if 'parameters' in grass_module:
            for param in grass_module['parameters']:
                if param in aggregated_keys.keys():
                    amkey = aggregated_keys[param]['amkey']
                    virtual_module_params[amkey] = grass_module['parameters'][param]

                    add_param_description(
                        virtual_module_params[amkey], param, aggregated_keys)

        if 'returns' in grass_module:
            for param in grass_module['returns']:
                if param in aggregated_keys.keys():
                    amkey = aggregated_keys[param]['amkey']
                    virtual_module_returns[amkey] = grass_module['returns'][param]

                    add_param_description(
                        virtual_module_returns[amkey], param, input_dict)

        if 'import_descr' in grass_module:
            for param in grass_module['import_descr']:
                for key, val in import_descr_dict.items():
                    if param == val:
                        virtual_module_params[key] = grass_module['import_descr'][val]

                        add_param_description(
                            virtual_module_params[key], 'import_descr_' + param, import_descr_dict)

        if 'exporter' in grass_module:
            for param in grass_module['exporter']:
                for key, val in exporter_dict.items():
                    if param == val:
                        virtual_module_returns[key] = grass_module['exporter'][val]

                        add_param_description(
                            virtual_module_returns[key], 'exporter' + param, exporter_dict)

    virtual_module = Module(
        id=pc_template['id'],
        description=pc_template['description'],
        categories=['actinia-module'],
        parameters=virtual_module_params,
        returns=virtual_module_returns
    )

    return virtual_module


def fillTemplateFromProcessChain(module):
    """ This method receives a process chain for an actinia module and loads
        the according process chain template. The received values will be
        replaced to be passed to actinia. In case the template has more
        placeholder values than it receives, the missing attribute is returned
        as string.
    """
    kwargs = {}
    inOrOutputs = []

    if module.get('inputs') is not None:
        inOrOutputs += module.get('inputs')

    if module.get('outputs') is not None:
        inOrOutputs += module.get('outputs')

    for item in inOrOutputs:
        if (item.get('param') is None) or (item.get('value') is None):
            return None
        key = item['param']
        val = item['value']
        kwargs[key] = val

    tpl_file = module["module"] + '.json'

    # find variables from processchain
    tpl_source = pcTplEnv.loader.get_source(pcTplEnv, tpl_file)[0]
    parsed_content = pcTplEnv.parse(tpl_source)
    undef = meta.find_undeclared_variables(parsed_content)

    for i in undef:
        if i not in kwargs.keys():
            log.error('Required parameter "' + i + '" not in process chain!')
            return i

    # fill process chain template
    tpl = pcTplEnv.get_template(tpl_file)
    pc_template = json.loads(tpl.render(**kwargs).replace('\n', ''))

    return (pc_template['template']['list'])
