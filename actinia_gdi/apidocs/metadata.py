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


Documentation objects for GNOS api endpoints
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import os
import json

from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel
from actinia_gdi.model.responseModels import GeodataResponseModel


script_dir = os.path.dirname(os.path.abspath(__file__))
null = "null"


connection_get_docs = {
    "summary": "Tests for active connection to Geonetwork opensource.",
    "description": "The request will ask the backend if it can successfully connect to Geonetwork.",
    "tags": [
        "GeoNetwork"
    ],
    "responses": {
        "200": {
            "description": "Success or failure of connection",
            "schema": SimpleStatusCodeResponseModel
        }
    }
}

connection_post_docs = {
    "summary": "Tests for active connection to Geonetwork opensource.",
    "description": "The request will ask the backend if it can successfully connect to Geonetwork.",
    "tags": [
        "GeoNetwork"
    ],
    "responses": {
        "200": {
            "description": "Success or failure of connection",
            "schema": SimpleStatusCodeResponseModel
        }
    }
}

rel_path = "../apidocs/examples/gnos_rawTags_get_example.json"
abs_file_path = os.path.join(script_dir, rel_path)
with open(abs_file_path) as jsonfile:
    rawTags_get_docs_example = json.load(jsonfile)

rawTags_get_docs = {
    "summary": "Requests one or many tags from Geonetwork opensource.",
    "description": "The request will ask Geonetwork which metadata records are available for a certain tag or more tags separated by comma and returns the JSON response with these records.",
    "tags": [
        "GeoNetwork"
    ],
    "parameters": [
        {
            "in": "path",
        "name": "tags",
        "type": "string",
        "description": "One or more Geonetwork tags, comma separated",
        "required": True
      }
    ],
    "responses": {
        "200": {
            "description": "The Search Results from Geonetwork",
            "schema": {
                "example": rawTags_get_docs_example
            }
        }
    }
}


rel_path = "../apidocs/examples/gnos_rawCategory_get_example.json"
abs_file_path = os.path.join(script_dir, rel_path)
with open(abs_file_path) as jsonfile:
    rawCategory_get_docs_example = json.load(jsonfile)

rawCategory_get_docs = {
    "summary": "Requests a category from Geonetwork opensource.",
    "description": "The request will ask Geonetwork which metadata records are available for a certain category and returns the JSON response with these records. Requirement: a virtual CSW is defined in Geonetwork",
    "tags": [
        "GeoNetwork"
    ],
    "parameters": [
        {
            "in": "path",
        "name": "category",
        "type": "string",
        "description": "A Geonetwork category",
        "required": True
      }
    ],
    "responses": {
        "200": {
            "description": "The Search Results from Geonetwork",
            "schema": {
                "example": rawCategory_get_docs_example
            }
        }
    }
}

rel_path = "../apidocs/examples/gnos_rawUuid_get_example.json"
abs_file_path = os.path.join(script_dir, rel_path)
with open(abs_file_path) as jsonfile:
    rawUuid_get_docs_example = json.load(jsonfile)

rawUuid_get_docs = {
    "summary": "Requests an uuid from Geonetwork opensource.",
    "description": "The request will ask Geonetwork which metadata records are available for a certain uuid and returns the JSON response with this record.",
    "tags": [
        "GeoNetwork"
    ],
    "parameters": [
        {
            "in": "path",
        "name": "uuid",
        "type": "string",
        "description": "A Geonetwork uuid from a record",
        "required": True
      }
    ],
    "responses": {
        "200": {
            "description": "The Search Results from Geonetwork",
            "schema": {
                "example": rawUuid_get_docs_example
            }
        }
    }
}


tags_get_docs = {
    "summary": "Get geodata object from requests to Geonetwork opensource by one or many tags.",
    "description": "The request will ask Geonetwork which metadata records are available for a certain tag or more tags separated by comma and returns a parsed record build from model. At the moment only the first record is returned.",
    "tags": [
        "GeoNetwork"
    ],
    "parameters": [
        {
            "in": "path",
        "name": "tags",
        "type": "string",
        "description": "One or more Geonetwork tags, comma separated",
        "required": True
      }
    ],
    "responses": {
        "200": {
            "description": "Modelled Search Results from Geonetwork",
            "schema": GeodataResponseModel
        }
    }
}


uuid_get_docs = {
    "summary": "Get geodata object from requests to Geonetwork opensource by uuid.",
    "description": "The request will ask Geonetwork which metadata records are available for a certain uuid and returns a parsed record build from model. At the moment only the first record is returned.",
    "tags": [
        "GeoNetwork"
    ],
    "parameters": [
        {
            "in": "path",
        "name": "uuid",
        "type": "string",
        "description": "A Geonetwork uuid from a record",
        "required": True
      }
    ],
    "responses": {
        "200": {
            "description": "Modelled Search Results from Geonetwork",
            "schema": GeodataResponseModel
        }
    }
}
