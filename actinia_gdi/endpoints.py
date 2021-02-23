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


Add endpoints to flask app with endpoint definitions and routes
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-2021 mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from flask import current_app, send_from_directory
import werkzeug

from actinia_gdi.resources.logging import log
from actinia_gdi.api.resources import Update

from actinia_gdi.api.processes.test import ActiniaCoreConnection
from actinia_gdi.api.processes.test import JobTestWrapper
from actinia_gdi.api.processes.test import JobHtmlTestWrapper
from actinia_gdi.api.processes.test import JobIdTestWrapper

from actinia_gdi.api.processes.loop import JobLoopWrapper
from actinia_gdi.api.processes.loop import JobHtmlLoopWrapper
from actinia_gdi.api.processes.loop import JobIdLoopWrapper
from actinia_gdi.api.processes.loop import JobIdCancelLoopWrapper

from actinia_gdi.api.processes.sentinel1 import JobS1Wrapper
from actinia_gdi.api.processes.sentinel1 import JobHtmlS1Wrapper
from actinia_gdi.api.processes.sentinel1 import JobIdS1Wrapper
from actinia_gdi.api.processes.sentinel1 import JobIdCancelS1Wrapper


# endpoints loaded if run as standalone app
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
    def static_content(filename):
        # WARNING: all content from folder "static" will be accessible!
        return send_from_directory(app.static_folder, filename)

    # ##### TEST actiniaCore
    # GET / POST
    apidoc.add_resource(ActiniaCoreConnection, '/processes/test/connection')
    # GET: list / POST: start job without writing into jobdb
    apidoc.add_resource(
        JobTestWrapper,
        '/processes/test/jobs'
    )
    # GET: list
    apidoc.add_resource(
        JobHtmlTestWrapper,
        '/processes/test/jobs.html'
    )
    # GET: read
    apidoc.add_resource(
        JobIdTestWrapper,
        '/processes/test/jobs/<jobid>'
    )

    # ##### Loop
    # GET: list / POST: create (start job)
    apidoc.add_resource(
        JobLoopWrapper,
        '/processes/loop/jobs'
    )
    # GET: list
    apidoc.add_resource(
        JobHtmlLoopWrapper,
        '/processes/loop/jobs.html'
    )
    # GET: read
    apidoc.add_resource(
        JobIdLoopWrapper,
        '/processes/loop/jobs/<jobid>'
    )
    # POST: cancel
    apidoc.add_resource(
        JobIdCancelLoopWrapper,
        '/processes/loop/jobs/<jobid>/operations/cancel'
    )

    # ##### sentinel1 actiniaCore
    # GET: list / POST: create (start job)
    apidoc.add_resource(
        JobS1Wrapper,
        '/processes/sentinel1/jobs'
    )
    # GET: list
    apidoc.add_resource(
        JobHtmlS1Wrapper,
        '/processes/sentinel1/jobs.html'
    )
    # GET: read
    apidoc.add_resource(
        JobIdS1Wrapper,
        '/processes/sentinel1/jobs/<jobid>'
    )
    # POST: cancel
    apidoc.add_resource(
        JobIdCancelS1Wrapper,
        '/processes/sentinel1/jobs/<jobid>/operations/cancel'
    )

    # #### WEBHOOK FROM ACTINIA-CORE
    # POST: trigger status update
    apidoc.add_resource(
        Update,
        '/resources/processes/operations/update'
    )

    # apidoc.add_resource(Actinia, '/actinia/<path:actinia_path>')
    # allows "/" inside variable
