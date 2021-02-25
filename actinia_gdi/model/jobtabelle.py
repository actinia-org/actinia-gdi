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


Model classes for jobtabelle
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from peewee import Model
from peewee import CharField, DateTimeField, AutoField
from playhouse.postgres_ext import BinaryJSONField
from playhouse.pool import PooledPostgresqlExtDatabase

from actinia_gdi.resources.config import JOBTABLE
from actinia_gdi.resources.logging import log


log.debug("Database config loaded: %s:%s/%s/%s.%s" % (
    JOBTABLE.host, JOBTABLE.port, JOBTABLE.database,
    JOBTABLE.schema, JOBTABLE.table))

"""database connection"""
jobdb = PooledPostgresqlExtDatabase(
    JOBTABLE.database, **{
        'host': JOBTABLE.host,
        'port': JOBTABLE.port,
        'user': JOBTABLE.user,
        'password': JOBTABLE.pw,
        'max_connections': 8,
        'stale_timeout': 300
    }
)


class BaseModel(Model):
    """Base Model for tables in jobdb
    """
    class Meta:
        database = jobdb


class Job(BaseModel):
    """Model for jobtable in database
    """
    idpk_jobs = AutoField()
    process = CharField(null=True)
    feature_type = CharField(null=True)
    rule_configuration = BinaryJSONField(null=True)
    job_description = BinaryJSONField(null=True)
    time_created = DateTimeField(null=True)
    time_started = DateTimeField(null=True)
    time_estimated = DateTimeField(null=True)
    time_ended = DateTimeField(null=True)
    metadata = CharField(null=True)
    status = CharField(null=True)
    actinia_core_response = BinaryJSONField(null=True)
    actinia_core_jobid = CharField(null=True)

    class Meta:
        table_name = JOBTABLE.table
        schema = JOBTABLE.schema
