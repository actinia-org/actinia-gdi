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


Endpoint definitions to manipulate processes
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import json

from flask import make_response, jsonify, request
from flask_restful import Resource

# from actinia_gdi.apidocs.processes import processes
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel
from actinia_gdi.core.processes import updateJob
from actinia_gdi.resources.logging import log


class Update(Resource):
    """ Definition for endpoint update
    @app.route('/resources/processes/operations/update')

    Contains HTTP POST endpoint updating a job
    Contains swagger documentation
    """

    def get(self):
        res = jsonify(SimpleStatusCodeResponseModel(
            status=405,
            message="Method Not Allowed"
        ))
        return make_response(res, 405)

    def head(self):
        return make_response('', 200)

    def post(self):
        """ Update a job

        This method is called by HTTP POST actinia-core webhook
        @app.route('/resources/processes/operations/update')
        This method is calling core method updateJob
        """

        postbody = request.get_json(force=True)

        if type(postbody) is dict:
            postbody = json.dumps(postbody)
        elif type(postbody) != 'str':
            postbody = str(postbody)

        actiniaCoreResp = json.loads(postbody)

        resourceID = actiniaCoreResp['resource_id']

        log.info("\n Received webhook call for " + resourceID)

        job = updateJob(resourceID, actiniaCoreResp)

        if job is not None:
            return make_response(jsonify(job), 200)
        else:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error'
                   )))
            return make_response(res, 404)
