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


Template loader file
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


from jinja2 import Environment, PackageLoader

# this environment is used for all cases where individual templates are loaded
tplEnv = Environment(
    loader=PackageLoader('actinia_gdi', 'templates')
)

# this environment is used for process chain templates only
pcTplEnv = Environment(
    loader=PackageLoader('actinia_gdi', 'templates/pc_templates')
)
