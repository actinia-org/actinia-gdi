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


Module to start a process
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-2021 mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import json

# from actinia_gdi.core.gnosWriter import update

from actinia_gdi.api.common import checkConnectionWithoutResponse
from actinia_gdi.resources.logging import log
from actinia_gdi.core.jobtable import insertNewJob, getJobById
from actinia_gdi.core.jobtable import getAllIds, getAllJobs, cancelJobById
from actinia_gdi.core.actiniaCore import postActiniaCore, cancelActiniaCore
from actinia_gdi.core.actiniaCore import parseActiniaIdFromUrl
from actinia_gdi.core.jobtable import updateJobByResourceID


def createJob(jsonDict, process):
    """ Method to parse prePC including fetching information from
    geonetwork and writing information to Jobtable
    as well as starting job in actinia-core

    This method can be called by HTTP POST
    @app.route('/processes/test/jobs')
    """

    prePC_orig = json.dumps(jsonDict)

    # TODO: define prePC (pre processchain) model if differs from pc
    # prePC = prePC(**jsonDict)
    # as we don't hava a model yet
    # prePC = json.dumps(jsonDict)

    connection = checkConnectionWithoutResponse('actinia-core')

    if connection is not None:
        actiniaCoreResp = postActiniaCore(
            process,
            jsonDict
        )
        log.debug(actiniaCoreResp)

        # try:
        #     prePCDict = prePC.to_struct()
        # except Exception as e:
        #     log.error('prePC is invalid!')
        #     log.error(e)
        #     return None

        job = insertNewJob(
            jsonDict,
            jsonDict,  # as we don't hava a model yet
            process,
            jsonDict.get('feature_type'),  # currently empty (polygon later)
            actiniaCoreResp
        )

        if actiniaCoreResp['status'] == 'error':
            log.error("Error start processing in actinia-core")
            resourceId = parseActiniaIdFromUrl(actiniaCoreResp['resource_id'])
            job = updateJob(resourceId, actiniaCoreResp)

        return job
    else:
        return None


def getJob(jobid):
    """ Method to read job from Jobtable by id

    This method can be called by HTTP GET
    @app.route('/processes/test/jobs/<jobid>')
    """

    job = getJobById(jobid)

    return job


def getAllJobIDs():
    """ Method to read all job ids from Jobtable

    This method can be called by HTTP GET
    @app.route('/processes/test/jobs.html')
    """

    job = getAllIds()

    return job


def getJobs(filters, process):
    """ Method to read all jobs from Jobtable with filter

    This method can be called by HTTP GET
    @app.route('/processes/test/jobs')
    """

    jobs = getAllJobs(filters, process)

    return jobs


def updateJob(resourceId, actiniaCoreResp):
    """ Method to update job in Jobtable

    This method is called by webhook endpoint
    """

    status = actiniaCoreResp['status']

    job, uuid, utcnow = updateJobByResourceID(
        resourceId,
        actiniaCoreResp,
        status
    )

    # TODO: for now if multiple records need to be updated, this
    # can be told by specifying multiple uuids comma-separated in the
    # "feature_uuid" field of the preprocesschain. This might change later...
    # if status == 'finished':
    #     try:
    #         uuids = uuid.split(',')
    #         for uuid in uuids:
    #             update(uuid, utcnow)
    #     except Exception:
    #         log.warning('Could not update geonetwork record')

    return job


def cancelJob(jobid):
    """ Method to cancel job from Jobtable by id

    This method can be called by HTTP POST
    @app.route('/processes/test/jobs/<jobid>/operations/cancel')
    """
    job = getJobById(jobid)
    if job is not None:
        log.debug('The job with jobid ' + str(jobid) + ' exists')
        status = job['status']
        resourceId = job['actinia_core_jobid']
        if not status or not resourceId:
            log.error('Job status or resourceId is not set!')
            return None
        else:
            log.debug('Job status is %s and resourceId is %s'
                      % (status, resourceId))

        connection = checkConnectionWithoutResponse('actinia-core')
        if connection is not None:
            if status in ['PENDING', 'RUNNING']:
                log.debug('Status is in PENDING or RUNNING, will cancel')
                res = cancelActiniaCore(resourceId)
                if res:
                    log.debug('Actinia-Core response TRUE')
                    job = cancelJobById(jobid)
                    log.debug('Job in jobtable is ' + job['status'])
                    return job
                else:
                    log.debug('Actinia-Core response is None')
                    return None
            else:
                log.debug('Status not in PENDING or RUNNING, pass')
                return job
        else:
            log.error('There is no connection to actinia-core')
            return None
    else:
        log.error('The job with jobid ' + str(jobid) + 'does not exist')
        return None
