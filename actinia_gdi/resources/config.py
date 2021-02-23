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


Configuration file
"""

__author__ = "Carmen Tawalika"
__copyright__ = "2018-present mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import configparser
import glob
from pathlib import Path

# config can be overwritten by mounting *.ini files into folders inside
# the config folder.
DEFAULT_CONFIG_PATH = "config"
CONFIG_FILES = [str(f) for f in Path(
    DEFAULT_CONFIG_PATH).glob('**/*.ini') if f.is_file()]
GENERATED_CONFIG = DEFAULT_CONFIG_PATH + '/actinia-gdi.cfg'


class APP:
    """Default config for app and api doc
    """
    version = '0.0.0'
    url = 'http://localhost:8080'


class JOBTABLE:
    """Default config for database connection for jobtabelle
    """
    host = 'localhost'
    port = '5432'
    database = 'gis'
    user = 'gis'
    pw = 'gis'
    schema = 'actinia'
    table = 'tab_jobs'
    id_field = 'idpk_jobs'


class GEONETWORK:
    """Default config for connection to geonetwork
    """
    scheme = 'http'
    host = 'localhost'
    port = '1234'
    base_path = '/geonetwork'
    csw_path = '/srv/eng/csw'
    csw_publication = '/srv/eng/csw-publication'
    user = 'test'
    password = 'test'
    csw_url = scheme + '://' + host + ':' + port + base_path + csw_path


class LOGCONFIG:
    """Default config for logging
    """
    logfile = 'actinia-gdi.log'
    level = 'DEBUG'
    type = 'stdout'


class ACTINIACORE:
    """Default config for actinia_core
    """
    url = 'http://localhost:1236/api/v1/'
    user = 'actinia'
    filestorage = ''
    password = 'actinia'
    esa_apihub_user = 'changeme'
    esa_apihub_pw = 'changeme'


class GISTABLE:
    """Default config for database connection for geodata database
    """
    host = 'localhost'
    port = '5432'
    database = 'gis'
    user = 'gis'


class FILEUPLOAD:
    geodata = '/tmp/'
    templates = '/tmp/'


class Configfile:

    def __init__(self):
        """
        This class will overwrite the config classes above when config files
        named DEFAULT_CONFIG_PATH/**/*.ini exist.
        On first import of the module it is initialized.
        """

        config = configparser.ConfigParser()
        config.read(CONFIG_FILES)

        if len(config) <= 1:
            print("Could not find any config file, using default values.")
            return
        print("Loading config files: " + str(CONFIG_FILES) + " ...")

        with open(GENERATED_CONFIG, 'w') as configfile:
            config.write(configfile)
        print("Configuration written to " + GENERATED_CONFIG)

        # APP
        if config.has_section("APP"):
            if config.has_option("APP", "version"):
                APP.version = config.get("APP", "version")
            if config.has_option("APP", "url"):
                APP.url = config.get("APP", "url")

        # JOBTABLE
        if config.has_section("JOBTABLE"):
            if config.has_option("JOBTABLE", "host"):
                JOBTABLE.host = config.get("JOBTABLE", "host")
            if config.has_option("JOBTABLE", "port"):
                JOBTABLE.port = config.get("JOBTABLE", "port")
            if config.has_option("JOBTABLE", "database"):
                JOBTABLE.database = config.get("JOBTABLE", "database")
            if config.has_option("JOBTABLE", "user"):
                JOBTABLE.user = config.get("JOBTABLE", "user")
            if config.has_option("JOBTABLE", "pw"):
                JOBTABLE.pw = config.get("JOBTABLE", "pw")
            if config.has_option("JOBTABLE", "schema"):
                JOBTABLE.schema = config.get("JOBTABLE", "schema")
            if config.has_option("JOBTABLE", "table"):
                JOBTABLE.table = config.get("JOBTABLE", "table")
            if config.has_option("JOBTABLE", "id_field"):
                JOBTABLE.id_field = config.get("JOBTABLE", "id_field")

        # GEONETWORK
        if config.has_section("GEONETWORK"):
            if config.has_option("GEONETWORK", "scheme"):
                GEONETWORK.scheme = config.get("GEONETWORK", "scheme")
            if config.has_option("GEONETWORK", "host"):
                GEONETWORK.host = config.get("GEONETWORK", "host")
            if config.has_option("GEONETWORK", "port"):
                GEONETWORK.port = config.get("GEONETWORK", "port")
            if config.has_option("GEONETWORK", "base_path"):
                GEONETWORK.base_path = config.get("GEONETWORK", "base_path")
            if config.has_option("GEONETWORK", "csw_path"):
                GEONETWORK.csw_path = config.get("GEONETWORK", "csw_path")
            if config.has_option("GEONETWORK", "csw_create_path"):
                GEONETWORK.csw_create_path = config.get("GEONETWORK", "csw_create_path")
            if config.has_option("GEONETWORK", "user"):
                GEONETWORK.user = config.get("GEONETWORK", "user")
            if config.has_option("GEONETWORK", "password"):
                GEONETWORK.password = config.get("GEONETWORK", "password")

            if (config.has_option("GEONETWORK", "scheme") and
                    config.has_option("GEONETWORK", "host") and
                    config.has_option("GEONETWORK", "port") and
                    config.has_option("GEONETWORK", "base_path") and
                    config.has_option("GEONETWORK", "csw_path")):

                GEONETWORK.csw_url = (GEONETWORK.scheme + '://' +
                                      GEONETWORK.host + ':' +
                                      GEONETWORK.port +
                                      GEONETWORK.base_path +
                                      GEONETWORK.csw_path)

            if (config.has_option("GEONETWORK", "scheme") and
                    config.has_option("GEONETWORK", "host") and
                    config.has_option("GEONETWORK", "port") and
                    config.has_option("GEONETWORK", "base_path") and
                    config.has_option("GEONETWORK", "csw_publication")):

                GEONETWORK.csw_publication = (GEONETWORK.scheme + '://' +
                                              GEONETWORK.host + ':' +
                                              GEONETWORK.port +
                                              GEONETWORK.base_path +
                                              GEONETWORK.csw_publication)

        # LOGGING
        if config.has_section("LOGCONFIG"):
            if config.has_option("LOGCONFIG", "logfile"):
                LOGCONFIG.logfile = config.get("LOGCONFIG", "logfile")
            if config.has_option("LOGCONFIG", "level"):
                LOGCONFIG.level = config.get("LOGCONFIG", "level")
            if config.has_option("LOGCONFIG", "type"):
                LOGCONFIG.type = config.get("LOGCONFIG", "type")

        # ACTINIACORE
        if config.has_section("ACTINIACORE"):
            if config.has_option("ACTINIACORE", "url"):
                ACTINIACORE.url = config.get("ACTINIACORE", "url")
            if config.has_option("ACTINIACORE", "user"):
                ACTINIACORE.user = config.get("ACTINIACORE", "user")
            if config.has_option("ACTINIACORE", "filestorage"):
                ACTINIACORE.filestorage = config.get("ACTINIACORE", "filestorage")
            if config.has_option("ACTINIACORE", "password"):
                ACTINIACORE.password = config.get("ACTINIACORE", "password")
            if config.has_option("ACTINIACORE", "esa_apihub_user"):
                ACTINIACORE.esa_apihub_user = config.get("ACTINIACORE", "esa_apihub_user")
            if config.has_option("ACTINIACORE", "esa_apihub_pw"):
                ACTINIACORE.esa_apihub_pw = config.get("ACTINIACORE", "esa_apihub_pw")

        # GISTABLE
        if config.has_section("GISTABLE"):
            if config.has_option("GISTABLE", "host"):
                GISTABLE.host = config.get("GISTABLE", "host")
            if config.has_option("GISTABLE", "port"):
                GISTABLE.port = config.get("GISTABLE", "port")
            if config.has_option("GISTABLE", "database"):
                GISTABLE.database = config.get("GISTABLE", "database")
            if config.has_option("GISTABLE", "user"):
                GISTABLE.user = config.get("GISTABLE", "user")

        # FILEUPLOAD
        if config.has_section("FILEUPLOAD"):
            if config.has_option("FILEUPLOAD", "geodata"):
                FILEUPLOAD.geodata = config.get("FILEUPLOAD", "geodata")
            if config.has_option("FILEUPLOAD", "templates"):
                FILEUPLOAD.templates = config.get("FILEUPLOAD", "templates")


init = Configfile()
