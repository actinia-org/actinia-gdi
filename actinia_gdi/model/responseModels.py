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


Common api methods
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from flask import jsonify
from flask_restful_swagger_2 import Schema


class SimpleStatusCodeResponseModel(Schema):
    """Simple response schema to inform about status.

    """
    type = 'object'
    properties = {
        'status': {
            'type': 'number',
            'description': 'The status code of the request.'
        },
        'message': {
            'type': 'string',
            'description': 'A short message to describes the status'
        }
    }
    required = ["status", "message"]


simpleResponseExample = SimpleStatusCodeResponseModel(status=200, message="success")
SimpleStatusCodeResponseModel.example = simpleResponseExample


class FileUploadResponseModel(Schema):
    """Simple response schema to inform about status.

    """
    type = 'object'
    properties = {
        'status': {
            'type': 'int',
            'description': 'The status code of the request.'
        },
        'message': {
            'type': 'string',
            'description': 'A short message to describes the status'
        },
        'name': {
            'type': 'string',
            'description': 'Name of the uploaded file'
        },
        'record': {
            'type': 'string',
            'description': 'Name of the metadata record'
        }
    }
    required = ["status", "message", "name"]


fileUploadResponseExample = FileUploadResponseModel(
    status=200,
    message="success",
    name="dd52427d-e703-44d9-a526-05b892e6a935.json",
    record=""
)
FileUploadResponseModel.example = fileUploadResponseExample


class GeodataResponseModel(Schema):
    """Model for object for geodata

    This object contains the metadata from GNOS
    """
    type = 'object'
    properties = {
        'uuid': {
            'type': 'string',
            'description': 'The Geonetwork uuid.'
        },
        'bbox': {
            'type': 'array',
            'items': {
                'type': 'number'
            },
            'minItems': 4,
            'maxItems': 4,
            'description': 'The bounding box of the result.'
        },
        'crs': {
            'type': 'string',
            'description': 'The coordinate reference system of the result.'
        },
        'table': {
            'type': 'string',
            'description': ('The database connection string of the source ' +
                            'of the result.')
        }
    }
    required = ["uuid", "bbox"]


geodataResponseExample = GeodataResponseModel(
    uuid="da165110-88fd-11da-a88f-000d939bc5d8",
    bbox=[51.1, -34.6, -17.3, 38.2],
    crs="urn:ogc:def:crs:::WGS 1984",
    table="http://www.fao.org/ag/AGL/aglw/aquastat/watresafrica/index.stm"
)
GeodataResponseModel.example = geodataResponseExample


class ExceptionTracebackModel(Schema):
    """Response schema that contains Exception information of the called endpoint
    in case an Exception was raised.

    This information is required to debug the REST API.
    """
    type = 'object'
    properties = {
        'message': {
            'type': 'string',
            'description': 'The message that was send with the Exception'
        },
        'type': {
            'type': 'string',
            'description': 'The type of the Exception'
        },
        'traceback': {
            'type': 'string',
            'description': 'The full traceback of the Exception'
        }
    }
    required = ["message", "type", "traceback"]

    example = {
        "message": "Error",
        "type": "exceptions.Exception",
        "traceback": "File \"main.py\", line 2, in <module>\n    raise" +
                     " Exception(\"Error\")\n"
    }
