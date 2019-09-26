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


Endpoint definitions for processes
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from flask import make_response, jsonify, request, render_template
from flask_restful import Resource
from flask_restful_swagger_2 import swagger

# from actinia_gdi.apidocs.processes import processes
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel
from actinia_gdi.core.processes import getAllJobIDs, getJobs
from actinia_gdi.core.processes import createJob, getJob
from actinia_gdi.core.processes import cancelJob
from actinia_gdi.resources.logging import log


class JobHtml(Resource):
    """ Definition for endpoint test
    @app.route('/processes/test/jobs')

    Contains HTTP GET endpoint listing all jobs
    Contains HTTP POST endpoint creating a new job
    Contains swagger documentation
    """

    # @swagger.doc(processes.jobs_getHtml_docs)
    def get(self):
        """ List all jobs

        This method is called by HTTP GET
        @app.route('/processes/test/jobs')
        This method is calling core method readJob
        """

        jobs = getAllJobIDs()

        return make_response(render_template(
            'response/list.html',
            resource="Process: 'test' - Jobs:",
            url=request.url,
            jobs=jobs
        ))

    def post(self):
        res = jsonify(SimpleStatusCodeResponseModel(
            status=405,
            message="Method Not Allowed"
        ))
        return make_response(res, 405)


class Job(Resource):
    """ Definition for endpoint test
    @app.route('/processes/test/jobs')

    Contains HTTP GET endpoint listing all jobs
    Contains HTTP POST endpoint creating a new job
    Contains swagger documentation
    """

    # @swagger.doc(processes.jobs_get_docs)
    def get(self):
        """ List all jobs

        This method is called by HTTP GET
        @app.route('/processes/test/jobs')
        This method is calling core method readJob
        """

        args = request.args
        process = request.path.split('/')[2]
        jobsArray = getJobs(args, process)

        jobs = {}
        jobs['jobs'] = jobsArray

        return make_response(jsonify(jobs))

    # @swagger.doc(processes.jobs_post_docs)
    def post(self):
        """ Create new job

        This method is called by HTTP POST
        @app.route('/processes/test/jobs')
        This method is calling core method createJob
        """
        log.info("\n Received HTTP POST with job:")
        print(request.get_json(force=True))

        # We determine the process type here, depending on which endpoint
        # was called

        process = request.path.split('/')[2]

        job = createJob(request.get_json(force=True), process)
        if job is not None:
            return make_response(jsonify(job), 201)
        else:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error'
                   )))
            return make_response(res, 404)


class JobId(Resource):
    """ Definition for endpoint test
    @app.route('/processes/test/jobs/<jobid>')

    Contains HTTP GET endpoint reading a job
    Contains swagger documentation
    """

    # @swagger.doc(processes.jobId_get_docs)
    def get(self, jobid):
        """ Wrapper method to receive HTTP call and pass it to function

        This method is called by HTTP GET
        @app.route('/processes/test/jobs/<jobid>')
        This method is calling core method readJob
        """
        if jobid is None:
            return make_response("Not found", 404)

        log.info("\n Received HTTP GET request for job with id " + str(jobid))

        job = getJob(jobid)

        if job is not None:
            return make_response(jsonify(job), 200)
        else:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Not Found: ' + request.url
                   )))
            return make_response(res, 404)

    def post(self):
        res = jsonify(SimpleStatusCodeResponseModel(
            status=405,
            message="Method Not Allowed"
        ))
        return make_response(res, 405)


class JobIdCancel(Resource):
    """ Definition for endpoint test
    @app.route('/processes/test/jobs/<jobid>/operations/cancel')

    Contains HTTP POST endpoint to cancel a job by the jobId
    Contains swagger documentation
    """

    def get(self):
        res = jsonify(SimpleStatusCodeResponseModel(
            status=405,
            message="Method Not Allowed"
        ))
        return make_response(res, 405)

    # @swagger.doc(processes.jobIdCancel_post_docs)
    def post(self, jobid):
        """ Wrapper method to cancel a job by using the jobId

        This method is called by HTTP POST
        @app.route('/processes/test/jobs/<jobid>/operations/cancel')
        This method is calling core method readJob
        """
        if jobid is None:
            return make_response("Not found", 404)

        log.info("\n Received HTTP POST request for job with id " + str(jobid)
                 + "to cancel the job")

        job = cancelJob(jobid)

        if job is not None:
            return make_response(jsonify(job), 200)
        else:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Not Found: ' + request.url
                   )))
            return make_response(res, 404)
