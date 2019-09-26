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


Endpoint definitions for gnos with swagger docs
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import json
from datetime import datetime

from flask import make_response, jsonify
from flask_restful import Resource
from flask_restful_swagger_2 import swagger

from actinia_gdi.apidocs import metadata
from actinia_gdi.api.common import checkConnection
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel
from actinia_gdi.core.gnosReader import getRecordsByCategory
from actinia_gdi.core.gnosReader import getRecordByUUID, getRecordsByTags
from actinia_gdi.core.gnosReader import getMetaByUUID, getMetaByTags
from actinia_gdi.core.gnosParser import makeItJson
from actinia_gdi.core.gnosWriter import update
from actinia_gdi.resources.logging import log


class GnosConnection(Resource):
    """ Definition for endpoint @app.route('metadata/test/connection')

    Contains HTTP GET endpoint
    Contains HTTP POST endpoint
    Contains swagger documentation
    """
    @swagger.doc(metadata.connection_get_docs)
    def get(self):
        return checkConnection('geonetwork')

    @swagger.doc(metadata.connection_post_docs)
    def post(self):
        return checkConnection('geonetwork')


class RawTags(Resource):
    """ Definition for endpoint @app.route('/metadata/raw/tags/<tags>')

    Contains HTTP GET endpoint
    Contains swagger documentation
    """
    @swagger.doc(metadata.rawTags_get_docs)
    def get(self, tags):
        try:
            gnosresp = getRecordsByTags(tags)
            records = makeItJson(gnosresp)

            res = make_response(records, 200)
            res.headers['Content-Type'] = 'application/json'
            return res
        except Exception:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error looking for tags "' + tags + '".'
                   )))
            return make_response(res, 404)


class RawCat(Resource):
    """ Definition for endpoint
    @app.route('/metadata/raw/categories/<category>')

    Contains HTTP GET endpoint
    Contains swagger documentation
    """
    @swagger.doc(metadata.rawCategory_get_docs)
    def get(self, category):
        try:
            gnosresp = getRecordsByCategory(category)
            records = makeItJson(gnosresp)

            res = make_response(records, 200)
            res.headers['Content-Type'] = 'application/json'
            return res
        # except TemplateNotFound as e:
        #     print('ERROR: ' + repr(e) + " - " + e.message)
        #     return make_response('Error looking for category "' + category +
        #                          '".', 404)
        except Exception as e:
            log.error('ERROR: ' + repr(e) + " - " + str(e))
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Category "' + category + '" not found.'
                   )))
            return make_response(res, 404)


class RawUuid(Resource):
    """ Definition for endpoint @app.route('/metadata/raw/uuids/<uuid>')

    Contains HTTP GET endpoint
    Contains swagger documentation
    """
    @swagger.doc(metadata.rawUuid_get_docs)
    def get(self, uuid):
        try:
            gnosresp = getRecordByUUID(uuid)
            record = makeItJson(gnosresp)
            # 47e7d99e-b227-4f80-8f4c-8ff1b5016c27

            res = make_response(record, 200)
            res.headers['Content-Type'] = 'application/json'
            return res
        except Exception:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error looking for uuid "' + uuid + '".'
                   )))
            return make_response(res, 404)


class Tags(Resource):
    """ Definition for endpoint @app.route('/metadata/geodata/tags/<tags>')

    Contains HTTP GET endpoint
    Contains swagger documentation
    """
    @swagger.doc(metadata.tags_get_docs)
    def get(self, tags):
        try:
            records = getMetaByTags(tags)
            res_json = json.dumps(records.to_struct())

            res = make_response(res_json, 200)
            res.headers['Content-Type'] = 'application/json'
            return res
        except Exception:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error looking for tags "' + tags + '".'
                   )))
            return make_response(res, 404)


class Uuid(Resource):
    """ Definition for endpoint @app.route('/metadata/geodata/uuids/<uuid>')

    Contains HTTP GET endpoint
    Contains swagger documentation
    """
    @swagger.doc(metadata.uuid_get_docs)
    def get(self, uuid):
        try:
            record = getMetaByUUID(uuid)
            # 47e7d99e-b227-4f80-8f4c-8ff1b5016c27
            res_json = json.dumps(record.to_struct())

            res = make_response(res_json, 200)
            res.headers['Content-Type'] = 'application/json'
            return res
        except Exception:
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error looking for uuid "' + uuid + '".'
                   )))
            return make_response(res, 404)


class UpdateUuid(Resource):
    """ Definition for endpoint @app.route('/metadata/update/uuids/<uuid>')
    TODO: not use in production environment

    Contains HTTP GET endpoint
    Contains swagger documentation
    """

    # @swagger.doc(metadata.uuid_get_docs)
    def get(self, uuid):

        try:
            utcnow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            gnosresp = update(uuid, utcnow)
            if gnosresp is None:
                raise Exception
            res = make_response(gnosresp.content, 200)
            return res
        except Exception as e:
            log.error('error parsing gnos response')
            log.error(e)
            res = (jsonify(SimpleStatusCodeResponseModel(
                        status=404,
                        message='Error looking for uuid "' + uuid + '".'
                   )))
            return make_response(res, 404)
