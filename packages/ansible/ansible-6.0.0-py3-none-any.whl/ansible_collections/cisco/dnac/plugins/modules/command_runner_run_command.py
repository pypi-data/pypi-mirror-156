#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: command_runner_run_command
short_description: Resource module for Command Runner Run Command
description:
- Manage operation create of the resource Command Runner Run Command.
- Submit request for read-only CLIs.
version_added: '3.1.0'
extends_documentation_fragment:
  - cisco.dnac.module
author: Rafael Campos (@racampos)
options:
  commands:
    description: Command Runner Run Command's commands.
    elements: str
    type: list
  description:
    description: Command Runner Run Command's description.
    type: str
  deviceUuids:
    description: Command Runner Run Command's deviceUuids.
    elements: str
    type: list
  name:
    description: Command Runner Run Command's name.
    type: str
  timeout:
    description: Command Runner Run Command's timeout.
    type: int
requirements:
- dnacentersdk >= 2.4.9
- python >= 3.5
notes:
  - SDK Method used are
    command_runner.CommandRunner.run_read_only_commands_on_devices,

  - Paths used are
    post /dna/intent/api/v1/network-device-poller/cli/read-request,

"""

EXAMPLES = r"""
- name: Create
  cisco.dnac.command_runner_run_command:
    dnac_host: "{{dnac_host}}"
    dnac_username: "{{dnac_username}}"
    dnac_password: "{{dnac_password}}"
    dnac_verify: "{{dnac_verify}}"
    dnac_port: "{{dnac_port}}"
    dnac_version: "{{dnac_version}}"
    dnac_debug: "{{dnac_debug}}"
    commands:
    - string
    description: string
    deviceUuids:
    - string
    name: string
    timeout: 0

"""

RETURN = r"""
dnac_response:
  description: A dictionary or list with the response returned by the Cisco DNAC Python SDK
  returned: always
  type: dict
  sample: >
    {
      "response": {
        "taskId": "string",
        "url": "string"
      },
      "version": "string"
    }
"""
