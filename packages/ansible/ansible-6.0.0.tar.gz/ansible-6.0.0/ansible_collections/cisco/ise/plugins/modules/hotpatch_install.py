#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: hotpatch_install
short_description: Resource module for Hotpatch Install
description:
- Manage operation create of the resource Hotpatch Install.
- >
   Triggers hot patch installation on the Cisco ISE node. A task ID is returned which can be used to monitor the progress of the hot patch installation
   process. As hot patch installation triggers the Cisco ISE to restart, the task API becomes unavailable for a certain period of time.
version_added: '2.1.0'
extends_documentation_fragment:
  - cisco.ise.module
author: Rafael Campos (@racampos)
options:
  hotpatchName:
    description: Hotpatch Install's hotpatchName.
    type: str
  repositoryName:
    description: Hotpatch Install's repositoryName.
    type: str
requirements:
- ciscoisesdk >= 2.0.1
- python >= 3.5
seealso:
- name: Cisco ISE documentation for Patching
  description: Complete reference of the Patching API.
  link: https://developer.cisco.com/docs/identity-services-engine/v1/#!patch-and-hot-patch-openapi
notes:
  - SDK Method used are
    patching.Patching.install_hotpatch,

  - Paths used are
    post /api/v1/hotpatch/install,

"""

EXAMPLES = r"""
- name: Create
  cisco.ise.hotpatch_install:
    ise_hostname: "{{ise_hostname}}"
    ise_username: "{{ise_username}}"
    ise_password: "{{ise_password}}"
    ise_verify: "{{ise_verify}}"
    hotpatchName: string
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
        "message": "string"
      },
      "version": "string"
    }
"""
