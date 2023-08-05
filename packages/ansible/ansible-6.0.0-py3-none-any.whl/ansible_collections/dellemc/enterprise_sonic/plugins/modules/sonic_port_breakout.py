#!/usr/bin/python
# -*- coding: utf-8 -*-
# © Copyright 2020 Dell Inc. or its subsidiaries. All Rights Reserved
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#############################################

"""
The module file for sonic_port_breakout
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
---
module: sonic_port_breakout
version_added: 1.0.0
notes:
- Tested against Enterprise SONiC Distribution by Dell Technologies.
- Supports C(check_mode).
author: Niraimadaiselvam M (@niraimadaiselvamm)
short_description: Configure port breakout settings on physical interfaces
description:
  - This module provides configuration management of port breakout parameters on devices running Enterprise SONiC.
options:
  config:
    description:
      - Specifies the port breakout related configuration.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Specifies the name of the port breakout.
        type: str
        required: true
      mode:
        description:
          - Specifies the mode of the port breakout.
        type: str
        choices:
          - 1x100G
          - 1x400G
          - 1x40G
          - 2x100G
          - 2x200G
          - 2x50G
          - 4x100G
          - 4x10G
          - 4x25G
          - 4x50G
  state:
    description:
      - Specifies the operation to be performed on the port breakout configured on the device.
      - In case of merged, the input mode configuration will be merged with the existing port breakout configuration on the device.
      - In case of deleted the existing port breakout mode configuration will be removed from the device.
    default: merged
    choices: ['merged', 'deleted']
    type: str
"""
EXAMPLES = """
# Using deleted
#
# Before state:
# -------------
#
#do show interface breakout
#-----------------------------------------------
#Port  Breakout Mode  Status        Interfaces
#-----------------------------------------------
#1/1   4x10G          Completed     Eth1/1/1
#                                   Eth1/1/2
#                                   Eth1/1/3
#                                   Eth1/1/4
#1/11  1x100G         Completed     Eth1/11
#

- name: Merge users configurations
  dellemc.enterprise_sonic.sonic_port_breakout:
    config:
      - name: 1/11
        mode: 1x100G
    state: deleted

# After state:
# ------------
#
#do show interface breakout
#-----------------------------------------------
#Port  Breakout Mode  Status        Interfaces
#-----------------------------------------------
#1/1   4x10G          Completed     Eth1/1/1
#                                   Eth1/1/2
#                                   Eth1/1/3
#                                   Eth1/1/4
#1/11  Default        Completed     Ethernet40


# Using deleted
#
# Before state:
# -------------
#
#do show interface breakout
#-----------------------------------------------
#Port  Breakout Mode  Status        Interfaces
#-----------------------------------------------
#1/1   4x10G          Completed     Eth1/1/1
#                                   Eth1/1/2
#                                   Eth1/1/3
#                                   Eth1/1/4
#1/11  1x100G         Completed     Eth1/11
#
- name: Merge users configurations
  dellemc.enterprise_sonic.sonic_port_breakout:
    config:
    state: deleted


# After state:
# ------------
#
#do show interface breakout
#-----------------------------------------------
#Port  Breakout Mode  Status        Interfaces
#-----------------------------------------------
#1/1   Default        Completed     Ethernet0
#1/11  Default        Completed     Ethernet40


# Using merged
#
# Before state:
# -------------
#
#do show interface breakout
#-----------------------------------------------
#Port  Breakout Mode  Status        Interfaces
#-----------------------------------------------
#1/1   4x10G          Completed     Eth1/1/1
#                                   Eth1/1/2
#                                   Eth1/1/3
#                                   Eth1/1/4
#
- name: Merge users configurations
  dellemc.enterprise_sonic.sonic_port_breakout:
    config:
      - name: 1/11
        mode: 1x100G
    state: merged


# After state:
# ------------
#
#do show interface breakout
#-----------------------------------------------
#Port  Breakout Mode  Status        Interfaces
#-----------------------------------------------
#1/1   4x10G          Completed     Eth1/1/1
#                                   Eth1/1/2
#                                   Eth1/1/3
#                                   Eth1/1/4
#1/11  1x100G         Completed     Eth1/11


"""
RETURN = """
before:
  description: The configuration prior to the model invocation.
  returned: always
  type: list
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
after:
  description: The resulting configuration model invocation.
  returned: when changed
  type: list
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample: ['command 1', 'command 2', 'command 3']
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.argspec.port_breakout.port_breakout import Port_breakoutArgs
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.config.port_breakout.port_breakout import Port_breakout


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=Port_breakoutArgs.argument_spec,
                           supports_check_mode=True)

    result = Port_breakout(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
