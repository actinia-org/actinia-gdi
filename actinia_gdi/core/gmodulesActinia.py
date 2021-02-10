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


Module management related to process chain templates
"""

__license__ = "Apache-2.0"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Carmen Tawalika"


import json
from jinja2 import meta, nodes
import re

from actinia_gdi.core.gmodulesProcessor import run_process_chain
from actinia_gdi.core.gmodulesParser import ParseInterfaceDescription
from actinia_gdi.model.gmodules import Module
from actinia_gdi.resources.templating import pcTplEnv
from actinia_gdi.resources.logging import log


def filter_func(name):
    ''' filter examples out of template folder
    '''

    if "example" not in name:
        return True
    return False


def get_path_from_pc_name(pc_name):
    """Find out path of a template

    Parameters
    ----------
    pc_name : string
        Name of template.

    Returns
    -------
    tplPath : string
        Path of template

    """

    tplPath = pc_name + '.json'

    # change path to template if in subdir
    for i in pcTplEnv.list_templates(filter_func=filter_func):
        if i.split('/')[-1] == tplPath:
            tplPath = i

    return tplPath


def get_template_undef(pc_name):
    """Find out placeholders of a template

    Parameters
    ----------
    pc_name : string
        Name of template.

    Returns
    -------
    undef : list
        List of placeholders of template

    """
    tplPath = get_path_from_pc_name(pc_name)

    # find variables from processchain and render template with variables
    tpl_source = pcTplEnv.loader.get_source(pcTplEnv, tplPath)[0]
    parsed_content = pcTplEnv.parse(tpl_source)
    # {'column_name', 'name'}
    undef = meta.find_undeclared_variables(parsed_content)
    return undef


def render_template(pc):

    tplPath = get_path_from_pc_name(pc)

    undef = get_template_undef(pc)

    kwargs = {}
    for i in undef:
        kwargs[i] = '{{ ' + i + ' }}'

    tpl = pcTplEnv.get_template(tplPath)
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
    if suffix not in moduleparameter['description']:
        moduleparameter['description'] += suffix

    # add comment if there is one in process chain template
    if param not in input_dict:
        for input_dict_key in input_dict:
            if param in input_dict_key:
                param = input_dict_key
    if param in input_dict and 'comment' in input_dict[param]:
        comment = input_dict[param]['comment']
        if comment not in moduleparameter['description']:
            moduleparameter['description'] += " - " + comment
            # moduleparameter['comment'] = comment


class ValuePlaceholder(object):
    """Object to collect attributes for all placeholder types. Might be later
    separated into ValuePlaceholder, ImporterPlaceholder, ...
    """

    def __init__(self, val, param, module, module_id):
        self.val = val  # '{{ db_connection }}'
        self.param = param  # input
        self.module = module  # v.import
        self.module_id = module_id  # import_training_data
        self.comment = None
        self.run_interface_descr = False
        self.enum = None

        # matches placeholder in longer value, e.g. in
        # 'res = if(input <= {{ my_values }}, 1, null() )'
        # beware that in general it is easier to make the whole value
        # a placeholder. Might be not possible for e.g. r.mapcalc
        self.placeholders = re.findall(r"\{\{(.*?)\}\}", str(self.val))
        self.placeholders = [x.strip(' ') for x in self.placeholders]
        self.key = self.module + '_' + self.param  # 'v.import_input'
        # 'import_training_data_input'
        self.uuid = self.module_id + '_' + self.param


class PlaceholderCollector(object):

    def __init__(self, resourceBaseSelf):
        self.aggregated_exes = []
        self.aggregated_vals = []
        self.input_dict = {}
        self.import_descr_dict = {}
        self.exporter_dict = {}
        self.count = 1
        self.vps = []
        self.resourceBaseSelf = resourceBaseSelf
        # array of child ModuleCollector instances if nested actiniamodule
        self.child_pcs = []
        self.nested_modules = []
        self.actiniamodules_list = []

        actiniamodules = createProcessChainTemplateList()
        for k in actiniamodules:
            self.actiniamodules_list.append(k['id'])

    def collect_value_placeholders(self, vp):

        # do not run interface description if module is
        # nested actiniamodule in actiniamodule
        if vp.module in self.actiniamodules_list:
            module_pc_tpl = render_template(vp.module)
            module_list_items = module_pc_tpl['template']['list']
            child_amc = PlaceholderCollector(self.resourceBaseSelf)
            self.nested_modules.append(vp)

            for item in module_list_items:
                child_amc.loop_list_items(item)
                self.child_pcs.append(child_amc)

            return

        self.vps.append(vp)
        self.aggregated_vals.append(vp.val)
        self.input_dict[vp.module_id]["run_interface_descr"] = True

        if len(vp.placeholders) == 1:
            self.input_dict[vp.module_id]["gparams"][vp.key] = {}
            self.input_dict[vp.module_id]["gparams"][vp.key]['amkey'] = vp.placeholders[0]
            if vp.comment is not None:
                self.input_dict[vp.module_id]["gparams"][vp.key]['comment'] = vp.comment
            if vp.enum is not None:
                self.input_dict[vp.module_id]["gparams"][vp.key]['enum'] = vp.enum
        else:
            for amkey in vp.placeholders:
                newkey = "%s_%s" % (vp.key, amkey)
                self.input_dict[vp.module_id]["gparams"][newkey] = {}
                self.input_dict[vp.module_id]["gparams"][newkey]['amkey'] = amkey
                if vp.comment is not None:
                    self.input_dict[vp.module_id]["gparams"][newkey]['comment'] = vp.comment
                if vp.enum is not None:
                    self.input_dict[vp.module_id]["gparams"][newkey]['enum'] = vp.enum

    def collect_im_and_exporter_placeholders(self, vp, j, im_or_export):
        for key, val in j[im_or_export].items():
            if '{{ ' in val and ' }}' in val:
                self.input_dict[vp.module_id]["run_interface_descr"] = True
                # TODO: check if only part of value can be placeholder
                stripval = val.strip('{{').strip('}}').strip(' ')
                if im_or_export == "import_descr":
                    self.import_descr_dict[stripval] = key
                else:
                    self.exporter_dict[stripval] = key

    def execute_interface_descr(self, vp):
        item_key = str(self.count)
        pc_item = {item_key: {"module": vp.module,
                              "interface-description": True}}
        response = run_process_chain(self.resourceBaseSelf, pc_item)
        xml_strings = response['process_log']
        self.count = self.count + 1
        self.input_dict[vp.module_id]['xml_string'] = xml_strings[0]['stdout']

    def loop_list_items(self, i):
        """Loop over each item in process chain list and search for all
        placeholders. Might be param of an executable or value of a
        grass_module param. Value of actinia_module param is also possible.

        Fills self.input_dict, self.import_descr_dict and self.exporter_dict
        and runs interface description for grass_modules.

        """

        # collect the "exec" list items
        if 'exe' in i and 'params' in i:
            for j in i['params']:
                if '{{ ' in j and ' }}' in j and j not in self.aggregated_exes:
                    ph = re.search(r"\{\{(.*?)\}\}", j).groups()[0].strip(' ')
                    if ph not in self.aggregated_exes:
                        self.aggregated_exes.append(ph)
            return

        module = i['module']
        module_id = i['id']

        # TODO: display this in module description?
        # if hasattr(i, 'comment'):
        #     comment = i['comment']

        inOrOutputs = []
        if i.get('inputs') is not None:
            inOrOutputs += i.get('inputs')
        if i.get('outputs') is not None:
            inOrOutputs += i.get('outputs')

        # run_interface_descr = False

        self.input_dict[module_id] = {}
        self.input_dict[module_id]["gparams"] = {}
        self.input_dict[module_id]["run_interface_descr"] = False

        # aggregate all keys where values are a variable (placeholder)
        # in the processchain template
        # only aggregate them if the template value differs
        for j in inOrOutputs:
            val = j['value']
            vp = ValuePlaceholder(val, j['param'], module, module_id)
            if 'comment' in j:
                vp.comment = j['comment']
            if 'enum' in j:
                vp.enum = j['enum']

            if ('{{ ' in val and ' }}' in val
                    and val not in self.aggregated_vals):
                self.collect_value_placeholders(vp)

            if 'import_descr' in j:
                self.collect_im_and_exporter_placeholders(vp, j, "import_descr")

            if 'exporter' in j:
                self.collect_im_and_exporter_placeholders(vp, j, "exporter")

        if self.input_dict[module_id]["run_interface_descr"]:
            self.execute_interface_descr(vp)
        else:
            del self.input_dict[module_id]


class PlaceholderTransformer(object):

    def __init__(self):
        self.vm_params = []  # parameter to build virtual module
        self.vm_returns = []  # return values for virtual module
        self.aggregated_keys = []
        self.used_amkeys = []
        self.used_importkeys = []
        self.used_exportkeys = []

    def populate_vm_params_and_returns(self, gm, pc):

        # shorten variables to maintain readability below
        self.aks = self.aggregated_keys

        if 'parameters' in gm:
            for gm_param_obj in gm['parameters']:
                param = gm_param_obj['name']
                for ak in self.aks:
                    if param not in ak:
                        continue
                    amkey = self.aks[ak]['amkey']
                    if amkey in self.used_amkeys:
                        continue
                    self.used_amkeys.append(amkey)
                    temp_dict = {}
                    for key in gm_param_obj.keys():
                        temp_dict[key] = gm_param_obj[key]
                    temp_dict['name'] = amkey
                    if (param in self.aks.keys()
                            and 'enum' in self.aks[param]):
                        enum = self.aks[param]['enum']
                        temp_dict['schema']['enum'] = enum
                    add_param_description(temp_dict, param, self.aks)
                    self.vm_params.append(temp_dict)

        if 'returns' in gm:
            for gm_return_obj in gm['returns']:
                param = gm_return_obj['name']
                if param in self.aks.keys():
                    amkey = self.aks[param]['amkey']
                    if amkey in self.used_amkeys:
                        continue
                    self.used_amkeys.append(amkey)
                    temp_dict = {}
                    for key in gm_return_obj.keys():
                        temp_dict[key] = gm_return_obj[key]
                    temp_dict['name'] = amkey
                    add_param_description(temp_dict, param, self.aks)
                    self.vm_returns.append(temp_dict)

        if 'import_descr' in gm:
            for gm_import_obj in gm['import_descr']:
                param = gm_import_obj['name']
                for key, val in pc.import_descr_dict.items():
                    if param == val:
                        if key in self.used_importkeys:
                            continue
                        self.used_importkeys.append(key)
                        temp_dict = {}
                        for k in gm_import_obj.keys():
                            temp_dict[k] = gm_import_obj[k]
                        temp_dict['name'] = key
                        add_param_description(
                            temp_dict, 'import_descr_' + param,
                            pc.import_descr_dict)
                        self.vm_params.append(temp_dict)

        if 'exporter' in gm:
            for gm_export_obj in gm['exporter']:
                param = gm_export_obj['name']
                for key, val in pc.exporter_dict.items():
                    if param == val:
                        if key in self.used_exportkeys:
                            continue
                        self.used_exportkeys.append(key)
                        temp_dict = {}
                        for k in gm_export_obj.keys():
                            temp_dict[k] = gm_export_obj[k]
                        temp_dict['name'] = key
                        add_param_description(
                            temp_dict, 'exporter' + param, pc.exporter_dict)
                        self.vm_returns.append(temp_dict)

    def transformPlaceholder(self, placeholderCollector):
        """Loops over moduleCollection filled by loop_list_items and enriches
        information with created grass_module interface description. Will
        populate self.vm_params and self.vm_returns
        to create the final ActiniaModuleDescription.
        """

        placeholderCollection = placeholderCollector.input_dict.items()

        for k, v in placeholderCollection:
            # case when nested actiniamodule
            if v['run_interface_descr'] == False:
                return
            xml_string = v['xml_string']
            self.aggregated_keys = v['gparams']

            grass_module = ParseInterfaceDescription(
                xml_string,
                keys=self.aggregated_keys.keys()
            )

            self.populate_vm_params_and_returns(
                grass_module, placeholderCollector)

        # add parameters from executable
        for param in placeholderCollector.aggregated_exes:
            exe_param = {}
            exe_param['description'] = 'Simple parameter from executable'
            exe_param['required'] = True
            exe_param['schema'] = {'type': 'string'}
            add_param_description(
                exe_param, 'exe', dict())
            self.vm_params[param] = exe_param


def createActiniaModule(resourceBaseSelf, processchain):
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

    pc_template = render_template(processchain)
    pc_template_list_items = pc_template['template']['list']
    undef = get_template_undef(processchain)

    pc = PlaceholderCollector(resourceBaseSelf)
    for i in pc_template_list_items:
        pc.loop_list_items(i)

    pt = PlaceholderTransformer()
    pt.transformPlaceholder(pc)

    vm_params = []
    vm_returns = []
    for i in pt.vm_params:
        vm_params.append(i['name'])
    for i in pt.vm_returns:
        vm_returns.append(i['name'])

    # case when nested actinia_module is found and no interface description
    # was run
    for undefitem in undef:
        if undefitem not in vm_params and undefitem not in vm_returns:
            child_pt = PlaceholderTransformer()
            for child_pc in pc.child_pcs:
                # this will populate child_pt.vm_params and child_pt.vm_returns
                child_pt.transformPlaceholder(child_pc)
            for nm in pc.nested_modules:
                # TODO: confirm that there cannot be multiple placeholders in
                # one value of an actinia_module (95% sure)
                if nm.placeholders[0] == undefitem:

                    for i in child_pt.vm_params:
                        if i['name'] == nm.param:
                            temp_dict = {}
                            for key in i.keys():
                                temp_dict[key] = i[key]
                            temp_dict['name'] = undefitem
                            pt.vm_params.append(temp_dict)

                    for i in child_pt.vm_returns:
                        if i['name'] == nm.param:
                            temp_dict = {}
                            for key in i.keys():
                                temp_dict[key] = i[key]
                            temp_dict['name'] = undefitem
                            pt.vm_returns.append(temp_dict)

    virtual_module = Module(
        id=pc_template['id'],
        description=pc_template['description'],
        categories=['actinia-module'],
        parameters=pt.vm_params,
        returns=pt.vm_returns
    )

    return virtual_module


def find_filters(ast):
    """Find all the nodes of a given type.  If the type is a tuple,
    the check is performed for any of the tuple items.
    Function from: https://stackoverflow.com/questions/55275399/how-to-get-variables-along-with-their-filter-name-from-jinja2-template
    """
    for child in ast.iter_child_nodes():
        if isinstance(child, nodes.Filter):
            yield child
        else:
            for result in find_filters(child):
                yield result


def filtered_variables(ast):
    """Return variables that have filters, along with their filters. might
    return duplicate variable names with different filters
    Function from: https://stackoverflow.com/questions/55275399/how-to-get-variables-along-with-their-filter-name-from-jinja2-template
    """
    results = []
    for i, node in enumerate(find_filters(ast)):
        filters = []
        f = node
        filters.append(f.name)
        while isinstance(f.node, nodes.Filter):
            f = f.node
            filters.append(f.name)
        filters.reverse()
        results.append((f.node.name, filters))
    return results


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

    # change path to template if in subdir
    for i in pcTplEnv.list_templates(filter_func=filter_func):
        if i.split('/')[-1] == tpl_file:
            tpl_file = i

    # find variables from processchain
    tpl_source = pcTplEnv.loader.get_source(pcTplEnv, tpl_file)[0]
    parsed_content = pcTplEnv.parse(tpl_source)
    undef = meta.find_undeclared_variables(parsed_content)

    # find default variables from processchain
    default_vars = []
    filtered_vars = filtered_variables(parsed_content)
    for filtered_var in filtered_vars:
        if 'default' in filtered_var[1]:
            default_vars.append(filtered_var[0])

    for i in undef:
        if i not in kwargs.keys() and not i in default_vars:
            log.error('Required parameter "' + i + '" not in process chain!')
            return i

    # fill process chain template
    tpl = pcTplEnv.get_template(tpl_file)
    pc_template = json.loads(tpl.render(**kwargs).replace('\n', ''))

    return (pc_template['template']['list'])
