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


Endpoint definitions for sentine1 processing
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from flask_restful_swagger_2 import swagger

# from actinia_gdi.apidocs.processes import loop  # TODO
from actinia_gdi.api.processes.processes import Job, JobHtml, JobId, JobIdCancel


class JobHtmlS1Wrapper(JobHtml):
    # @swagger.doc(loop.jobs_getHtml_docs)
    def get(self):
        return super(JobHtmlS1Wrapper, self).get()

    # no docs because 405
    def post(self):
        return super(JobHtmlS1Wrapper, self).post()


class JobS1Wrapper(Job):
    # @swagger.doc(loop.jobs_get_docs)
    def get(self):
        return super(JobS1Wrapper, self).get()

    # @swagger.doc(loop.jobs_post_docs)
    def post(self):
        return super(JobS1Wrapper, self).post()


class JobIdS1Wrapper(JobId):
    # @swagger.doc(loop.jobId_get_docs)
    def get(self, jobid):
        return super(JobIdS1Wrapper, self).get(jobid)

    # no docs because 405
    def post(self):
        return super(JobIdS1Wrapper, self).post()


class JobIdCancelS1Wrapper(JobIdCancel):
    # no docs because 405
    def get(self):
        return super(JobIdCancelS1Wrapper, self).get()

    # @swagger.doc(loop.jobIdCancel_post_docs)
    def post(self, jobid):
        return super(JobIdCancelS1Wrapper, self).post(jobid)
