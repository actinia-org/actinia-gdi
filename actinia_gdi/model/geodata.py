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


Model classes for geodata object
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from jsonmodels import models, fields


class GeodataMeta(models.Base):
    """Model for geodata object

    This object contains the metadata from GNOS
    """
    uuid = fields.StringField()  # string
    bbox = fields.ListField([int, float])  # bbox array
    crs = fields.StringField()  # string
    table = fields.StringField()  # string
    format = fields.StringField()  # string
