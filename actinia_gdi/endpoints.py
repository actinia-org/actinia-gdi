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


Add endpoints to flask app with endpoint definitios and routes
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from flask import current_app, send_from_directory
import werkzeug

from actinia_gdi.resources.logging import log

from actinia_gdi.api.files import Upload
from actinia_gdi.api.metadata import GnosConnection
from actinia_gdi.api.metadata import RawTags
from actinia_gdi.api.metadata import RawCat
from actinia_gdi.api.metadata import RawUuid
from actinia_gdi.api.metadata import Tags
from actinia_gdi.api.metadata import Uuid



def addEndpoints(app, apidoc):
    @app.route('/')
    def index():
        try:
            return current_app.send_static_file('index.html')
        except werkzeug.exceptions.NotFound:
            log.debug('No index.html found in static folder. Serving backup.')
            return ("""<h1 style='color:red'>actinia-gdi</h1>
                <a href="latest/api/swagger.json">API docs</a>""")

    @app.route('/<path:filename>')
    def staticContent(filename):
        # WARNING: all content from folder "static" will be accessible!
        return send_from_directory(app.static_folder, filename)

    apidoc.add_resource(Upload, '/files')

    apidoc.add_resource(GnosConnection, '/metadata/test/connection')

    apidoc.add_resource(RawTags,     '/metadata/raw/tags/<tags>')
    apidoc.add_resource(RawCat,     '/metadata/raw/categories/<category>')
    apidoc.add_resource(RawUuid,    '/metadata/raw/uuids/<uuid>')
    apidoc.add_resource(Tags,        '/metadata/geodata/tags/<tags>')
    apidoc.add_resource(Uuid,       '/metadata/geodata/uuids/<uuid>')
