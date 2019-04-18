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


Module to communicate with jobtable
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from datetime import datetime

from playhouse.shortcuts import model_to_dict
from peewee import Expression, AutoField
from flask import current_app

from actinia_gdi.model.jobtabelle import Job, jobdb
from actinia_gdi.resources.config import JOBTABLE
from actinia_gdi.resources.logging import log
from actinia_gdi.core.actiniaCore import parseActiniaAsyncStatusResponse
from actinia_gdi.core.actiniaCore import parseActiniaIdFromUrl


# We used `jobdb.connect(reuse_if_open=True)` at the beginning
# of every method. Now we use `with jobdb:` as described in the
# peewee docs but we still try to jobdb.close() at the end of
# each method.

def initJobDB():
    """Create jobtable on startup."""
    Job.create_table(safe=True)
    log.debug('Created jobtable if not exists')


def smallifyResp(resp):
    smallRes = dict()
    smallRes['message'] = resp.get('message', None)
    smallRes['process_results'] = resp.get('process_results', None)
    smallRes['progress'] = resp.get('progress', None)
    smallRes['time_delta'] = resp.get('time_delta', None)
    # TODO: this will certainly break....
    smallRes['urls.resources'] = resp.get('urls.resources', None)
    return smallRes


def insertNewJob(
        rule_configuration,
        job_description,
        process,
        feature_type,
        actiniaCoreResp
        ):
    """Insert new job into jobtabelle.

    Args:
      rule_configuration (dict): original preProcessChain
      job_description (TODO): enriched preProcessChain with geometadata

    Returns:
      record (dict): the new record

    """
    utcnow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    actiniaCoreJobUrl = parseActiniaAsyncStatusResponse(
        actiniaCoreResp,
        "urls.status"
    )
    actiniaCoreJobID = parseActiniaIdFromUrl(actiniaCoreJobUrl)

    if current_app.debug is False:
        smallRes = dict()
        smallRes['message'] = actiniaCoreResp.get('message', None)
        smallRes['process_results'] = actiniaCoreResp.get('process_results', None)
        actiniaCoreResp = smallRes

        # actiniaCoreResp = smallifyResp(actiniaCoreResp)
    # TODO: test in debug, then remove
    # actiniaCoreResp = smallifyResp(actiniaCoreResp)

    job = Job(**{
        'rule_configuration': rule_configuration,
        'job_description': job_description,
        'status': 'PENDING',
        'time_created': utcnow,
        'process': process,
        'feature_type': feature_type,
        'actinia_core_response': actiniaCoreResp,
        'actinia_core_jobid': actiniaCoreJobID
    })

    with jobdb:
        job.save()

        queryResult = Job.select().where(Job.time_created == utcnow).get()

    record = model_to_dict(queryResult)

    log.info("Created new job with id " + str(record['idpk_jobs']) + ".")

    jobdb.close()

    return record


def getJobById(jobid):
    """ Method to read job from jobtabelle by id

    Args:
    jobid (int): id of job

    Returns:
    record (dict): the record matching the id
    """
    try:
        with jobdb:
            queryResult = Job.select().where(
                getattr(Job, JOBTABLE.id_field) == jobid).get()
        record = model_to_dict(queryResult)
        log.info("Information read from jobtable for job with id "
                 + str(record['idpk_jobs']) + ".")

    except Job.DoesNotExist:
        record = None

    jobdb.close()

    return record


def getAllIds():
    """ Method to read all jobs from jobtabelle

    Args: -

    Returns:
    jobIds (list): the record matching the id
    """
    with jobdb:
        queryResult = Job.select(getattr(Job, JOBTABLE.id_field)).dicts()

    jobIds = []

    # iterating reopens db connection!!
    for i in queryResult:
        jobIds.append(i[JOBTABLE.id_field])

    log.debug("Information read from jobtable.")

    jobdb.close()

    return jobIds


def getAllJobs(filters, process):
    """ Method to read all jobs from jobtabelle with filter

    Args: filters (ImmutableMultiDict): the args from the HTTP call

    Returns:
    jobs (list): the records matching the filter
    """
    log.debug('Received query for jobs')

    if process == 'test':
        query = Expression('a', '=', 'a')
    else:
        query = Expression(getattr(Job, 'process'), '=', process)

    if filters:
        log.debug("Found filters: " + str(filters))
        keys = [key for key in filters]

        for key in keys:

            try:
                getattr(Job, key)
            except Exception as e:
                log.warning(str(e))
                continue

            log.debug("Filter " + str(key)
                      + " with value " + str(filters[key]))

            if isinstance(getattr(Job, key), AutoField):
                try:
                    int(filters[key])
                except Exception as e:
                    log.error(str(e))
                    jobdb.close()
                    return

            try:
                # even though operators are listed as == and & in peewee docs,
                # for Expression creation use '=' and 'AND'.
                exp = Expression(getattr(Job, key), '=', filters[key])
                query = Expression(query, 'AND', exp)
            except AttributeError as e:
                log.error(str(e))

    with jobdb:
        queryResult = Job.select().where(query).dicts()

    jobs = []
    # iterating reopens db connection!!
    for i in queryResult:
        jobs.append(i)

    log.info("Found " + str(len(jobs)) + " results for query.")

    jobdb.close()

    return jobs


def cancelJobById(jobid):
    """ Method to change the status of a job to 'TERMINATED' in the jobtabelle
    by using its jobid

    Args:
    jobid (int): id of job

    Returns:
    record (dict): the record matching the id
    """
    utcnow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    try:
        with jobdb:
            queryResult = Job.select().where(
                getattr(Job, JOBTABLE.id_field) == jobid).get()
        record = model_to_dict(queryResult)
        log.debug("Information read from jobtable.")
    except Job.DoesNotExist:
        record = None
    try:
        query = Job.update(
            status='TERMINATED',
            time_ended=utcnow
        ).where(
            getattr(Job, JOBTABLE.id_field) == jobid
        )
        with jobdb:
            query.execute()
            queryResult2 = Job.select().where(
                getattr(Job, JOBTABLE.id_field) == jobid).get()
        record = model_to_dict(queryResult2)
    except Exception as e:
        log.error('Could not set the status to "TERMINATED" '
                  + 'and the time_ended in the jobtable.')
        log.error(str(e))
        record = None

    log.info("Information updated in jobtable for job with id "
             + str(record['idpk_jobs']) + ".")

    jobdb.close()

    return record


def updateJobByResourceID(resourceId, resp, status):
    """ Method to update job in jobtabelle when processing status changed

    Args:
    resourceId (str): actinia-core resourceId
    resp (dict): actinia-core response
    status (string): actinia-core processing status

    Returns:
    updatedRecord (TODO): the updated record
    """
    utcnow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        with jobdb:
            queryResult = Job.select().where(
                getattr(Job, 'actinia_core_jobid') == resourceId).get()
        record = model_to_dict(queryResult)
        log.debug("Information read from jobtable for job with id "
                  + str(record['idpk_jobs']) + ".")
    except Job.DoesNotExist:
        log.warning("Job does not exist and can therefore not be updated")
        return None, None, None

    # actinia-gdi_["PENDING", "RUNNING", "SUCCEES", "ERROR", "TERMINATED"]
    # actinia-core [accepted, running, finished, error, terminated]

    try:
        log.debug("Update status to " + status + " for job with id "
                  + str(record['idpk_jobs']) + ".")

        gdiStatus = record['status']

        try:
            gnosUuid = record['job_description']['feature_uuid']
        except Exception:
            log.warning('Feature has no uuid')
            gnosUuid = None

        if current_app.debug is False:
            smallRes = dict()
            smallRes['message'] = resp.get('message', None)
            smallRes['process_results'] = resp.get('process_results', None)
            resp = smallRes

            # resp = smallifyResp(resp)
        # TODO: test in debug, then remove
        # resp = smallifyResp(resp)

        if status == 'accepted':
            log.debug('Status already set to "PENDING"')
            return record, gnosUuid, utcnow

        elif status == 'running':
            if gdiStatus == 'RUNNING':
                log.debug('Status already set to "RUNNING"')
                return record, gnosUuid, utcnow

            query = Job.update(
                status='RUNNING',
                actinia_core_response=resp,
                time_started=utcnow
                # TODO: check if time_estimated can be set
                # time_estimated=
            ).where(
                getattr(Job, 'actinia_core_jobid') == resourceId
            )

        elif status in ['finished', 'error', 'terminated']:

            if status == 'finished':
                gdiStatus = 'SUCCESS'
            elif status == 'error':
                gdiStatus = 'ERROR'
            elif status == 'terminated':
                gdiStatus = 'TERMINATED'

            query = Job.update(
                status=gdiStatus,
                actinia_core_response=resp,
                time_ended=utcnow
            ).where(
                getattr(Job, 'actinia_core_jobid') == resourceId
            )

        else:
            log.error('Could not set the status to actinia-core status:'
                      + status + '(Status not found.)')
            return None, None, None

        with jobdb:
            query.execute()
            queryResult = Job.select().where(
                getattr(Job, 'actinia_core_jobid') == resourceId).get()

        record = model_to_dict(queryResult)
    except Exception as e:
        log.error('Could not set the status to actinia-core status: ' + status)
        log.error(str(e))
        return None, None, None

    log.info("Updated status to " + status + " for job with id "
             + str(record['idpk_jobs']) + ".")

    jobdb.close()

    return record, gnosUuid, utcnow
