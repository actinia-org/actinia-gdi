#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2018-2021 mundialis GmbH & Co. KG

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Redis server actinia_module interface
"""

__license__ = "Apache-2.0"
__author__ = "Carmen Tawalika"
__copyright__ = "Copyright 2021, mundialis"
__maintainer__ = "Carmen Tawalika"


from actinia_core.resources.common.redis_base import RedisBaseInterface
import pickle


class RedisActiniaModuleInterface(RedisBaseInterface):
    """The Redis actinia_module database interface

    A single actinia_module is stored as Hash with:
        - actinia_module id aka actinia_module name that must be unique
        - actinia-module dictionary

    In addition is the actinia_module_id saved in a hash that contains all
    actinia_module ids.
    """

    # We use two databases:
    # The actinia_module ID and the actinia_module name database
    # The actinia_module ID and actinia_module name databases are hashes
    actinia_module_id_hash_prefix = "ACTINIA-MODULE-ID-HASH-PREFIX::"
    actinia_module_id_db = "ACTINIA-MODULE-ID-DATABASE"

    def __init__(self):
        RedisBaseInterface.__init__(self)

    def create(self, actinia_module):
        """
        Add an actinia_module to the actinia_module database

        Args:
            actinia_module (dict): A dictionary of permissions

        Returns:
            bool:
            True is success, False if actinia_module is already in the database
        """
        actinia_module_id = actinia_module['id']

        keyname = self.actinia_module_id_hash_prefix + actinia_module_id
        if self.redis_server.exists(keyname) is True:
            return False

        actinia_module_bytes = pickle.dumps(actinia_module)
        mapping = {"actinia_module_id": actinia_module_id,
                   "actinia_module": actinia_module_bytes}

        lock = self.redis_server.lock(
            name="add_actinia_module_lock", timeout=1)
        lock.acquire()
        # First add the actinia_module-id to the actinia_module id database
        self.redis_server.hset(
            self.actinia_module_id_db, actinia_module_id, actinia_module_id)

        self.redis_server.hset(
            self.actinia_module_id_hash_prefix + actinia_module_id,
            mapping=mapping)
        lock.release()

        return True

    def read(self, actinia_module_id):
        """Return the actinia_module

        HGET actinia_module-id actinia_module_group

        Args:
            actinia_module_id: The actinia_module id

        Returns:
             str:
             The actinia_module group
        """

        try:
            actinia_module = pickle.loads(self.redis_server.hget(
                self.actinia_module_id_hash_prefix + actinia_module_id,
                "actinia_module"))
        except:
            return False

        return actinia_module

    def update(self, actinia_module_id, actinia_module):
        """Update the actinia_module.

        Renaming an entry is not allowed, only existing entries with the
        same actinia_module_id can be updated.

        Args:
            actinia_module_id (str): The actinia_module id
            actinia_module (dict): The actinia_module as dictionary

        Returns:
            bool:
            True is success, False if actinia_module is not in the database

        """
        keyname = self.actinia_module_id_hash_prefix + actinia_module_id
        if self.redis_server.exists(keyname) is False:
            return False

        actinia_module_bytes = pickle.dumps(actinia_module)
        mapping = {"actinia_module_id": actinia_module_id,
                   "actinia_module": actinia_module_bytes}

        lock = self.redis_server.lock(
            name="update_actinia_module_lock", timeout=1)
        lock.acquire()

        self.redis_server.hset(
            self.actinia_module_id_hash_prefix + actinia_module_id,
            mapping=mapping)

        lock.release()

        return True

    def delete(self, actinia_module_id):
        """Remove an actinia_module id from the database

        Args:
            actinia_module_id (str): The actinia_module id

        Returns:
            bool:
            True is actinia_module exists, False otherwise
        """
        if self.exists(actinia_module_id) == 0:
            return False

        lock = self.redis_server.lock(
            name="delete_actinia_module_lock", timeout=1)
        lock.acquire()
        # Delete the entry from the actinia_module id database
        self.redis_server.hdel(self.actinia_module_id_db, actinia_module_id)
        # Delete the actual actinia_module entry
        self.redis_server.delete(
            self.actinia_module_id_hash_prefix + actinia_module_id)
        lock.release()

        return True

    def list_all_ids(self):
        """
        List all actinia_module id's that are in the database

        HKEYS on the actinia_module id database

        Returns:
            list:
            A list of all actinia_module ids in the database
        """
        values = []
        list = self.redis_server.hkeys(self.actinia_module_id_db)
        for entry in list:
            if entry:
                entry = entry.decode()
            values.append(entry)

        return values

    def exists(self, actinia_module_id):
        """Check if the actinia_module is in the database

        Args:
            actinia_module_id (str): The actinia_module id

        Returns:
            bool:
            True is actinia_module exists, False otherwise
        """
        return self.redis_server.exists(
            self.actinia_module_id_hash_prefix + actinia_module_id)


# Create the Redis interface instance
redis_actinia_module_interface = RedisActiniaModuleInterface()
