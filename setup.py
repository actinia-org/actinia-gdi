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


Setup file for actinia_gdi.

This file was generated with PyScaffold 3.0.2.
PyScaffold helps you to put up the scaffold of your new Python project.
Learn more under: http://pyscaffold.org/
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "TODO"


from setuptools import setup

entry_points = {
  'console_scripts': [
    'name = actinia_gdi.resources.cli:name',
    'about = actinia_gdi.resources.cli:about',
    'pc2grass = actinia_gdi.resources.cli:pc2grass'
  ]
}


def setup_package():
    setup(setup_requires=['pyscaffold>=3.0a0,<3.1a0'],
          entry_points=entry_points,
          packages=['actinia_gdi'],
          package_dir={'actinia_gdi': 'actinia_gdi'},
          include_package_data=True,
          use_pyscaffold=True)


if __name__ == "__main__":
    setup_package()
