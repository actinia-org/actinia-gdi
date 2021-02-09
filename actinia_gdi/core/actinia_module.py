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
__copyright__ = "Copyright 2021, mundialis"
__maintainer__ = "Carmen Tawalika"


from actinia_gdi.core.redis_actinia_module import redis_actinia_module_interface
from actinia_core.resources.common.config import Configuration


def connect():
    conf = Configuration()
    try:
        conf.read()
    except:
        pass

    server = conf.REDIS_SERVER_URL
    port = conf.REDIS_SERVER_PORT
    if conf.REDIS_SERVER_PW:
        redis_password = conf.REDIS_SERVER_PW
    else:
        redis_password = None

    redis_actinia_module_interface.connect(
        host=server, port=port, password=redis_password)

    return redis_actinia_module_interface


def readAllActiniaModules():
    '''
    Get all actinia modules from redis database
    '''
    redis_actinia_module_interface = connect()
    actinia_module = redis_actinia_module_interface.list_all_ids()

    return actinia_module


def createActiniaModule(pc_tpl):
    '''
    Insert actinia module into database
    '''
    redis_actinia_module_interface = connect()
    actinia_module = redis_actinia_module_interface.create(pc_tpl)

    return actinia_module


def readActiniaModule(module_id):
    '''
    Get actinia module by id
    '''
    redis_actinia_module_interface = connect()
    actinia_module = redis_actinia_module_interface.read(module_id)

    return actinia_module


def updateActiniaModule(module_id, pc_tpl):
    '''
    Update actinia module by id
    '''
    redis_actinia_module_interface = connect()
    actinia_module = redis_actinia_module_interface.update(module_id, pc_tpl)

    return actinia_module


def deleteActiniaModule(module_id):
    '''
    Delete actinia module by id
    '''
    redis_actinia_module_interface = connect()
    actinia_module = redis_actinia_module_interface.delete(module_id)

    return actinia_module
