#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: backup_config
short_description: Resource module for Backup Config
description:
- Manage operation create of the resource Backup Config.
- Triggers on demand configuration backup on the ISE node. The API returns the task ID. Use the Task Service status API to get the status of the backup job.
version_added: '1.0.0'
extends_documentation_fragment:
  - cisco.ise.module
author: Rafael Campos (@racampos)
options:
  backupEncryptionKey:
    description: The encyption key for the backed up file. Encryption key must satisfy
      the following criteria - Contains at least one uppercase letter A-Z, Contains
      at least one lowercase letter a-z, Contains at least one digit 0-9, Contain only
      A-Za-z0-9_#, Has at least 8 characters, Has not more than 15 characters, Must
      not contain 'CcIiSsCco', Must not begin with.
    type: str
  backupName:
    description: The backup file will get saved with this name.
    type: str
  repositoryName:
    description: Name of the configured repository where the generated backup file will
      get copied.
    type: str
requirements:
- ciscoisesdk >= 2.0.1
- python >= 3.5
seealso:
- name: Cisco ISE documentation for Backup And Restore
  description: Complete reference of the Backup And Restore API.
  link: https://developer.cisco.com/docs/identity-services-engine/v1/#!backup-and-restore-open-api
notes:
  - SDK Method used are
    backup_and_restore.BackupAndRestore.config_backup,

  - Paths used are
    post /api/v1/backup-restore/config/backup,

"""

EXAMPLES = r"""
- name: Create
  cisco.ise.backup_config:
    ise_hostname: "{{ise_hostname}}"
    ise_username: "{{ise_username}}"
    ise_password: "{{ise_password}}"
    ise_verify: "{{ise_verify}}"
    backupEncryptionKey: string
    backupName: string
    repositoryName: string

"""

RETURN = r"""
ise_response:
  description: A dictionary or list with the response returned by the Cisco ISE Python SDK
  returned: always
  type: dict
  sample: >
    {
      "response": {
        "id": "string",
        "message": "string",
        "link": {
          "rel": "string",
          "href": "string",
          "type": "string"
        }
      },
      "version": "string"
    }
"""
