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


Endpoint definitions for test processes
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import json

from flask import make_response, jsonify, request
from flask_restful import Resource
from flask_restful_swagger_2 import swagger

# from actinia_gdi.apidocs.processes import test
from actinia_gdi.api.common import checkConnection
from actinia_gdi.api.processes.processes import Job, JobHtml, JobId
from actinia_gdi.core.actiniaCore import postActiniaCore
from actinia_gdi.core.actiniaCore import shortenActiniaCoreResp
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel
from actinia_gdi.resources.logging import log


class ActiniaCoreConnection(Resource):
    """ Definition for endpoint @app.route('/processes/test/connection')

    Contains HTTP GET endpoint
    Contains HTTP POST endpoint
    Contains swagger documentation
    """
    # @swagger.doc(test.connection_get_docs)
    def get(self):
        return checkConnection('actinia-core')

    # @swagger.doc(test.connection_post_docs)
    def post(self):
        return checkConnection('actinia-core')


class JobHtmlTestWrapper(JobHtml):
    # @swagger.doc(test.jobs_getHtml_docs)
    def get(self):
        return super(JobHtmlTestWrapper, self).get()

    # no docs because 405
    def post(self):
        return super(JobHtmlTestWrapper, self).post()


class JobTestWrapper(Job):
    # @swagger.doc(test.jobs_get_docs)
    def get(self):
        return super(JobTestWrapper, self).get()

    # @swagger.doc(test.processing_post_docs)
    def post(self):
        log.debug("Received HTTP POST with process: \n"
                  + json.dumps(request.get_json(force=True),
                               indent=4, sort_keys=True))

        try:
            fullResp = postActiniaCore(
                'test',
                request.get_json(force=True)
            )
            resp = shortenActiniaCoreResp(fullResp)

            if resp is None or fullResp['status'] == 'error':
                res = jsonify(SimpleStatusCodeResponseModel(
                    status=500,
                    message="failure"
                ))
                return make_response(res, 500)
            else:
                res = make_response(json.dumps(resp), 200)
                res.headers['Content-Type'] = 'application/json'
                return res
        except Exception:
            res = jsonify(SimpleStatusCodeResponseModel(status=500, message="failure"))
            return make_response(res, 500)


class JobIdTestWrapper(JobId):
    # @swagger.doc(test.jobId_get_docs)
    def get(self, jobid):
        return super(JobIdTestWrapper, self).get(jobid)

    # no docs because 405
    def post(self):
        return super(JobIdTestWrapper, self).post()
