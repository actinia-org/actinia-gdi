#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2018-present mundialis GmbH & Co. KG

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Module to communicate with actinia_core
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from actinia_gdi.resources.config import APP
from actinia_gdi.resources.config import GISTABLE
from actinia_gdi.resources.config import ACTINIACORE
from actinia_gdi.resources.templating import tplEnv
from actinia_gdi.resources.logging import log


def buildPCConnectionString(prePCTable):

    log.debug('Creating db connection string from "' + prePCTable + '"')
    # 'HOST=123;PORT=5432;DB=test;SCHEMA=actinia;TABLE=point'

    class DBClass():
        db = GISTABLE.database
        host = GISTABLE.host
        port = GISTABLE.port
        user = GISTABLE.user
        schema = ''
        table = ''

    dbInstance = DBClass()

    for kvp in prePCTable.split(';'):

        key = kvp.split('=')[0]
        val = kvp.split('=')[1]

        if key == 'SCHEMA':
            dbInstance.schema = val
        if key == 'TABLE':
            dbInstance.table = val

    pcConnectionString = ("PG:dbname=" + dbInstance.db
                          + " host=" + dbInstance.host
                          + " port=" + dbInstance.port
                          + " active_schema=" + dbInstance.schema
                          + " user=" + dbInstance.user)

    table = dbInstance.table

    log.debug("Created db connection string: " + pcConnectionString
              + " - table: " + table)
    # ('PG:dbname=gis host=localhost port=5555 active_schema=actinia
    #   user=actinia', 'points_for_testing')
    return pcConnectionString, table


def buildLoop(preProcessChain):

    webhookUrl = APP.url + "/resources/processes/operations/update"
    log.debug("Registering own webhook endpoint: " + str(webhookUrl))

    tpl = tplEnv.get_template(
        'actiniaCore/pc_loop.json'
    )

    class PCInputClass():
        param = ''
        value = ''

    pcInputs = []

    # Feature: transform input table information to grass connection string
    # try:
    #     preProcessChainTableFeat = preProcessChain.feature_source.table
    # except AttributeError as e:
    #     log.error(e)
    #     log.error("Feature has no data source")
    #     return
    #
    # if preProcessChainTableFeat is None:
    #     log.error("Feature has no data source")
    #     return
    #
    # connString = buildPCConnectionString(preProcessChainTableFeat)
    # feat_db = connString[0]
    # feat_layer = connString[1]

    proc = preProcessChain.procs[0]

    for input in proc.input:

        inputType = getattr(input, "type", None)

        if inputType == 'PARAMETER':
            pcInputObject = PCInputClass()
            pcInputObject.param = input.name
            path = ACTINIACORE.filestorage + '/' + input.value[0]
            pcInputObject.value = path
            pcInputs.append(pcInputObject)

        elif input.table:
            if input.name in ['a', 'b', 'c']:
                pcInputObject = PCInputClass()
                pcInputObject.param = input.name
                pcInputObject.value = input.value
                pcInputs.append(pcInputObject)

        else:
            log.error("Don't know what to do with input.")

    if (pcInputs is None or webhookUrl is None):
        log.error('Could not set all variables to replace in template.')
        return None

    postbody = tpl.render(
        inputs=pcInputs,
        webhookUrl=webhookUrl
    ).replace('\n', '')

    return postbody


def buildPCDummy(preProcessChain):

    webhookUrl = APP.url + "/resources/processes/operations/update"
    log.debug("Registering own webhook endpoint: " + str(webhookUrl))

    tpl = tplEnv.get_template('actiniaCore/pc_point_in_polygon.json')

    point = preProcessChain.get('point')
    polygon = preProcessChain.get('polygon')

    if polygon is None or point is None or webhookUrl is None:
        log.error('Could not set all variables to replace in template.')
        return None

    postbody = tpl.render(
        point=point,
        polygon=polygon,
        webhookUrl=webhookUrl
    ).replace('\n', '')

    return postbody


def buildPCS1Grd(preProcessChain):

    processType = preProcessChain.get('processType')
    if processType != 'preprocessing':
        log.error('process type is unknown')
        return None

    webhookUrl = APP.url + "/resources/processes/operations/update"
    log.debug("Registering own webhook endpoint: " + str(webhookUrl))

    tpl = tplEnv.get_template('actiniaCore/pc_r.s1.grd_template.json')

    user = ACTINIACORE.esa_apihub_user
    pw = ACTINIACORE.esa_apihub_pw
    S1A_name = preProcessChain.get('title')
    raw_path = ACTINIACORE.filestorage + '/' + 'sentinel1/raw/'
    preprocessing_path = (ACTINIACORE.filestorage + '/'
                          + 'sentinel1/preprocessing/')

    if (user is None
            or pw is None
            or S1A_name is None
            or raw_path is None
            or preprocessing_path is None
            or webhookUrl is None
            ):
        log.error('Could not set all variables to replace in template.')
        return None

    postbody = tpl.render(
        user=user,
        pw=pw,
        S1A_name=S1A_name,
        raw_path=raw_path,
        preprocessing_path=preprocessing_path,
        webhookUrl=webhookUrl
    ).replace('\n', '')

    return postbody
