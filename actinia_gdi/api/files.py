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


import os
import uuid

from flask import request, make_response, jsonify
from flask_restful import Resource
from flask_restful_swagger_2 import swagger
from werkzeug.utils import secure_filename

from actinia_gdi.apidocs import files
from actinia_gdi.resources.config import FILEUPLOAD
from actinia_gdi.core.gnosWriter import create
from actinia_gdi.model.responseModels import SimpleStatusCodeResponseModel
from actinia_gdi.model.responseModels import FileUploadResponseModel
from actinia_gdi.resources.logging import log


class Upload(Resource):
    """ Definition for endpoint @app.route('metadata/test/connection')

    Contains HTTP POST endpoint
    Contains swagger documentation
    """

    def get(self):
        res = jsonify(SimpleStatusCodeResponseModel(
            status=405,
            message="Method Not Allowed"
        ))
        return make_response(res, 405)

    @swagger.doc(files.upload_post_docs)
    def post(self):

        jsonFile = request.form.get('jsonFile')
        geodataFile = request.files.get('geodataFile')

        if not os.path.isdir(FILEUPLOAD.geodata):
            os.makedirs(FILEUPLOAD.geodata)

        # See file operations here:
        # https://www.programiz.com/python-programming/file-operation

        if geodataFile:
            # will be stored under original filename with uuid
            filename = (str(uuid.uuid4()) + '.'
                        + secure_filename(geodataFile.filename))
            geodataFile.save(FILEUPLOAD.geodata + '/' + filename)
            log.info('Received json file, saved to '
                     + FILEUPLOAD.geodata + '/' + filename)
        elif jsonFile:
            # will be stored under random name, e.g.
            # 5f82730c-f804-4e34-9c24-faaed902fab5.json
            filename = str(uuid.uuid4()) + '.json'
            with open(FILEUPLOAD.geodata + '/' + filename, 'x') as file:
                file.write(jsonFile)
            log.info('Received binary file, saved to '
                     + FILEUPLOAD.geodata + '/' + filename)
        else:
            log.error('No file found in postbody')

        metadatarecord = create(filename)

        res = jsonify(FileUploadResponseModel(
            status=200,
            message="Upload success",
            name=filename,
            record=metadatarecord
        ))
        res.headers['Access-Control-Allow-Origin'] = '*'
        return make_response(res, 200)
