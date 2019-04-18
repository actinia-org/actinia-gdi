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


Module to create and edit in geonetwork
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import os

import requests
import xmltodict

from actinia_gdi.core.common import auth
from actinia_gdi.resources.config import GEONETWORK
from actinia_gdi.resources.config import FILEUPLOAD
from actinia_gdi.resources.logging import log
from actinia_gdi.resources.templating import tplEnv


def create(filename):
    """ Method to get create metadata records in geonetwork

    """

    url = GEONETWORK.csw_publication
    recordtpl = tplEnv.get_template('geonetwork/template_metadaten.xml')
    record = recordtpl.render(title=filename).replace('\n', '')
    recordfs = recordtpl.render(title=filename)
    postbodytpl = tplEnv.get_template('geonetwork/post_create_record.xml')
    postbody = postbodytpl.render(metadata_record=record).replace('\n', '')
    postbodyfs = postbodytpl.render(metadata_record=recordfs)
    headers = {'content-type': 'application/xml; charset=utf-8'}

    log.info('Creating metadata record')

    try:
        gnosresp = requests.post(
            url,
            data=postbody,
            headers=headers,
            auth=auth(GEONETWORK)
        )

    except requests.exceptions.ConnectionError:
        return None

    if not os.path.isdir(FILEUPLOAD.templates):
        os.makedirs(FILEUPLOAD.templates)

    with open(FILEUPLOAD.templates + '/' + filename + '_template.xml',
              'x') as file:
        file.write(postbodyfs)
    log.info('Received binary file, saved to '
             + FILEUPLOAD.templates + '/' + filename + '_template.xml')

    try:
        parsedresp = xmltodict.parse(gnosresp.content)
        insertRes = parsedresp['csw:TransactionResponse']['csw:InsertResult']
        uuid = insertRes['csw:BriefRecord']['identifier']
        log.info('GNOS response is: ' + str(parsedresp))
        return uuid
    except Exception:
        return None
