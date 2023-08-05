#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
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
The module file for iosxr_lag_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = """
module: iosxr_lag_interfaces
short_description: LAG interfaces resource module
description:
- This module manages the attributes of LAG/Ether-Bundle interfaces on IOS-XR devices.
version_added: 1.0.0
notes:
- This module works with connection C(network_cli). See L(the IOS-XR Platform Options,../network/user_guide/platform_iosxr.html).
author: Nilashish Chakraborty (@NilashishC)
options:
  config:
    description: A provided Link Aggregation Group (LAG) configuration.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Name/Identifier of the LAG/Ether-Bundle to configure.
        type: str
        required: true
      members:
        description:
          - List of member interfaces for the LAG/Ether-Bundle.
        type: list
        elements: dict
        suboptions:
          member:
            description:
              - Name of the member interface.
            type: str
          mode:
            description:
              - Specifies the mode of the operation for the member interface.
              - Mode 'active' runs LACP in active mode.
              - Mode 'on' does not run LACP over the port.
              - Mode 'passive' runs LACP in passive mode over the port.
              - Mode 'inherit' runs LACP as configured in the bundle.
            type: str
            choices: ["on", "active", "passive", "inherit"]
      mode:
        description:
          - LAG mode.
          - Mode 'active' runs LACP in active mode over the port.
          - Mode 'on' does not run LACP over the port.
          - Mode 'passive' runs LACP in passive mode over the port.
        type: str
        choices: ["on", "active", "passive"]
      links:
        description:
          - This dict contains configurable options related to LAG/Ether-Bundle links.
        type: dict
        suboptions:
          max_active:
            description:
              - Specifies the limit on the number of links that can be active in the LAG/Ether-Bundle.
              - Refer to vendor documentation for valid values.
            type: int
          min_active:
            description:
              - Specifies the minimum number of active links needed to bring up the LAG/Ether-Bundle.
              - Refer to vendor documentation for valid values.
            type: int
      load_balancing_hash:
        description:
          - Specifies the hash function used for traffic forwarded over the LAG/Ether-Bundle.
          - Option 'dst-ip' uses the destination IP as the hash function.
          - Option 'src-ip' uses the source IP as the hash function.
        type: str
        choices: ["dst-ip", "src-ip"]
  running_config:
    description:
    - This option is used only with state I(parsed).
    - The value of this option should be the output received from the IOS-XR device
      by executing the command B(show running-config int).
    - The state I(parsed) reads the configuration from C(running_config) option and
      transforms it into Ansible structured data as per the resource module's argspec
      and the value is then returned in the I(parsed) key within the result.
    type: str
  state:
    description:
      - The state of the configuration after module completion.
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - deleted
      - parsed
      - rendered
      - gathered
    default: merged

"""
EXAMPLES = """
# Using merged
#
#
# ------------
# Before state
# ------------
#
# RP/0/0/CPU0:iosxr01#show run int
# Sun Jul  7 19:42:59.416 UTC
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description "GigabitEthernet - 1"
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
# !
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
# !
#
#
- name: Merge provided configuration with device configuration
  cisco.iosxr.iosxr_lag_interfaces:
    config:
    - name: Bundle-Ether10
      members:
      - member: GigabitEthernet0/0/0/1
        mode: inherit
      - member: GigabitEthernet0/0/0/3
        mode: inherit
      mode: active
      links:
        max_active: 5
        min_active: 2
      load_balancing_hash: src-ip

    - name: Bundle-Ether12
      members:
      - member: GigabitEthernet0/0/0/2
        mode: passive
      - member: GigabitEthernet0/0/0/4
        mode: passive
      load_balancing_hash: dst-ip
    state: merged
#
#
# -----------
# After state
# -----------
#
# RP/0/0/CPU0:iosxr01#show run int
# Sun Jul  7 20:51:17.685 UTC
# interface Bundle-Ether10
#  lacp mode active
#  bundle load-balancing hash src-ip
#  bundle maximum-active links 5
#  bundle minimum-active links 2
# !
# interface Bundle-Ether12
#  bundle load-balancing hash dst-ip
# !
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description 'GigabitEthernet - 1"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
#   bundle id 12 mode passive
# !
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
#  bundle id 12 mode passive
# !
#


# Using replaced
#
#
# -------------
# Before state
# -------------
#
#
# RP/0/0/CPU0:iosxr01#sho run int
# Sun Jul  7 20:58:06.527 UTC
# interface Bundle-Ether10
#  lacp mode active
#  bundle load-balancing hash src-ip
#  bundle maximum-active links 5
#  bundle minimum-active links 2
# !
# interface Bundle-Ether12
#  bundle load-balancing hash dst-ip
# !
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description 'GigabitEthernet - 1"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
#  bundle id 12 mode passive
# !
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
#  bundle id 12 mode passive
# !
#
#
- name: Replace device configuration of listed Bundles with provided configurations
  cisco.iosxr.iosxr_lag_interfaces:
    config:
    - name: Bundle-Ether12
      members:
      - name: GigabitEthernet0/0/0/2
      mode: passive

    - name: Bundle-Ether11
      members:
      - name: GigabitEthernet0/0/0/4
      load_balancing_hash: src-ip
    state: replaced
#
#
# -----------
# After state
# -----------
#
#
# RP/0/0/CPU0:iosxr01#sh run int
# Sun Jul  7 21:22:27.397 UTC
# interface Bundle-Ether10
#  lacp mode active
#  bundle load-balancing hash src-ip
#  bundle maximum-active links 5
#  bundle minimum-active links 2
# !
# interface Bundle-Ether11
#  bundle load-balancing hash src-ip
# !
# interface Bundle-Ether12
#  lacp mode passive
# !
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description 'GigabitEthernet - 1"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
#  bundle id 12 mode on
# !
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
#  bundle id 11 mode on
# !
#
#


# Using overridden
#
#
# ------------
# Before state
# ------------
#
#
# RP/0/0/CPU0:iosxr01#sh run int
# Sun Jul  7 21:22:27.397 UTC
# interface Bundle-Ether10
#  lacp mode active
#  bundle load-balancing hash src-ip
#  bundle maximum-active links 5
#  bundle minimum-active links 2
# !
# interface Bundle-Ether11
#  bundle load-balancing hash src-ip
# !
# interface Bundle-Ether12
#  lacp mode passive
# !
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description 'GigabitEthernet - 1"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
#  bundle id 12 mode on
# !
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
#  bundle id 11 mode on
# !
#
#

- name: Overrides all device configuration with provided configuration
  cisco.iosxr.iosxr_lag_interfaces:
    config:
    - name: Bundle-Ether10
      members:
      - member: GigabitEthernet0/0/0/1
        mode: inherit
      - member: GigabitEthernet0/0/0/2
        mode: inherit
      mode: active
      load_balancing_hash: dst-ip
    state: overridden
#
#
# ------------
# After state
# ------------
#
#
# RP/0/0/CPU0:iosxr01#sh run int
# Sun Jul  7 21:43:04.802 UTC
# interface Bundle-Ether10
#  lacp mode active
#  bundle load-balancing hash dst-ip
# !
# interface Bundle-Ether11
# !
# interface Bundle-Ether12
# !
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description 'GigabitEthernet - 1"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
# !
#
#


# Using deleted
#
#
# ------------
# Before state
# ------------
#
# RP/0/0/CPU0:iosxr01#sh run int
# Sun Jul  7 21:22:27.397 UTC
# interface Bundle-Ether10
#  lacp mode active
#  bundle load-balancing hash src-ip
#  bundle maximum-active links 5
#  bundle minimum-active links 2
# !
# interface Bundle-Ether11
#  bundle load-balancing hash src-ip
# !
# interface Bundle-Ether12
#  lacp mode passive
# !
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description 'GigabitEthernet - 1"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
#  bundle id 12 mode on
# !n
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
#  bundle id 11 mode on
# !
#
#

- name: Delete attributes of given bundles and removes member interfaces from them
    (Note - This won't delete the bundles themselves)
  cisco.iosxr.iosxr_lag_interfaces:
    config:
    - name: Bundle-Ether10
    - name: Bundle-Ether11
    - name: Bundle-Ether12
    state: deleted

#
#
# ------------
# After state
# ------------
#
# RP/0/0/CPU0:iosxr01#sh run int
# Sun Jul  7 21:49:50.004 UTC
# interface Bundle-Ether10
# !
# interface Bundle-Ether11
# !
# interface Bundle-Ether12
# !
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description 'GigabitEthernet - 1"
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
# !
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
# !
#
#

# Using deleted (without config)
#
#
# ------------
# Before state
# ------------
#
# RP/0/0/CPU0:an-iosxr#sh run int
# Sun Aug 18 19:49:51.908 UTC
# interface Bundle-Ether10
#  lacp mode active
#  bundle load-balancing hash src-ip
#  bundle maximum-active links 10
#  bundle minimum-active links 2
# !
# interface Bundle-Ether11
#  bundle load-balancing hash dst-ip
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/0
#  shutdown
# !
# interface GigabitEthernet0/0/0/1
#  bundle id 10 mode inherit
#  shutdown
# !
# interface GigabitEthernet0/0/0/2
#  bundle id 10 mode passive
#  shutdown
# !
# interface GigabitEthernet0/0/0/3
#  bundle id 11 mode passive
#  shutdown
# !
# interface GigabitEthernet0/0/0/4
#  bundle id 11 mode passive
#  shutdown
# !
#

- name: Delete attributes of all bundles and removes member interfaces from them (Note
    - This won't delete the bundles themselves)
  cisco.iosxr.iosxr_lag_interfaces:
    state: deleted

#
#
# ------------
# After state
# ------------
#
#
# RP/0/0/CPU0:an-iosxr#sh run int
# Sun Aug 18 19:54:22.389 UTC
# interface Bundle-Ether10
# !
# interface Bundle-Ether11
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 10.8.38.69 255.255.255.0
# !
# interface GigabitEthernet0/0/0/0
#  shutdown
# !
# interface GigabitEthernet0/0/0/1
#  shutdown
# !
# interface GigabitEthernet0/0/0/2
#  shutdown
# !
# interface GigabitEthernet0/0/0/3
#  shutdown
# !
# interface GigabitEthernet0/0/0/4
#  shutdown
# !

# Using parsed:

# parsed.cfg

# interface Bundle-Ether10
#  lacp mode active
#  bundle load-balancing hash src-ip
#  bundle maximum-active links 5
#  bundle minimum-active links 2
# !
# interface Bundle-Ether12
#  bundle load-balancing hash dst-ip
# !
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description 'GigabitEthernet - 1"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
#   bundle id 12 mode passive
# !
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
#  bundle id 12 mode passive
# !
#
- name: Convert lag interfaces config to argspec without connecting to the appliance
  cisco.iosxr.iosxr_lag_interfaces:
    running_config: "{{ lookup('file', './parsed.cfg') }}"
    state: parsed

# --------------
# Output
# --------------
#   parsed:
#     - name: Bundle-Ether10
#       members:
#         - member: GigabitEthernet0/0/0/1
#           mode: inherit
#         - member: GigabitEthernet0/0/0/3
#           mode: inherit
#       mode: active
#       links:
#         max_active: 5
#         min_active: 2
#       load_balancing_hash: src-ip

#     - name: Bundle-Ether12
#       members:
#         - member: GigabitEthernet0/0/0/2
#           mode: passive
#         - member: GigabitEthernet0/0/0/4
#           mode: passive
#       load_balancing_hash: dst-ip

# using gathered

# Device Config:
# -------------

# interface Bundle-Ether10
#  lacp mode active
#  bundle load-balancing hash src-ip
#  bundle maximum-active links 5
#  bundle minimum-active links 2
# !
# interface Bundle-Ether12
#  bundle load-balancing hash dst-ip
# !
# interface Loopback888
#  description test for ansible
#  shutdown
# !
# interface MgmtEth0/0/CPU0/0
#  ipv4 address 192.0.2.11 255.255.255.0
# !
# interface GigabitEthernet0/0/0/1
#  description 'GigabitEthernet - 1"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/2
#  description "GigabitEthernet - 2"
#   bundle id 12 mode passive
# !
# interface GigabitEthernet0/0/0/3
#  description "GigabitEthernet - 3"
#  bundle id 10 mode inherit
# !
# interface GigabitEthernet0/0/0/4
#  description "GigabitEthernet - 4"
#  bundle id 12 mode passive
# !
#

- name: Gather IOSXR lag interfaces configuration
  cisco.iosxr.iosxr_lag_interfaces:
    config:
    state: gathered

# --------------
# Output
# --------------
#   gathered:
#     - name: Bundle-Ether10
#       members:
#         - member: GigabitEthernet0/0/0/1
#           mode: inherit
#         - member: GigabitEthernet0/0/0/3
#           mode: inherit
#       mode: active
#       links:
#         max_active: 5
#         min_active: 2
#       load_balancing_hash: src-ip

#     - name: Bundle-Ether12
#       members:
#         - member: GigabitEthernet0/0/0/2
#           mode: passive
#         - member: GigabitEthernet0/0/0/4
#           mode: passive
#       load_balancing_hash: dst-ip

# Using rendered:
- name: Render platform specific commands from task input using rendered state
  cisco.iosxr.iosxr_lag_interfaces:
    config:
    - name: Bundle-Ether10
      members:
      - member: GigabitEthernet0/0/0/1
        mode: inherit
      - member: GigabitEthernet0/0/0/3
        mode: inherit
      mode: active
      links:
        max_active: 5
        min_active: 2
      load_balancing_hash: src-ip

    - name: Bundle-Ether12
      members:
      - member: GigabitEthernet0/0/0/2
        mode: passive
      - member: GigabitEthernet0/0/0/4
        mode: passive
      load_balancing_hash: dst-ip
    state: rendered

# Output:

# rendered:
#    [
#         - "interface Bundle-Ether10"
#         - " lacp mode active"
#         - " bundle load-balancing hash src-ip"
#         - " bundle maximum-active links 5"
#         - " bundle minimum-active links 2"
#         - "interface Bundle-Ether12"
#         - " bundle load-balancing hash dst-ip"
#         - "interface Loopback888"
#         - " description test for ansible"
#         - " shutdown"
#         - "interface MgmtEth0/0/CPU0/0"
#         - " ipv4 address 192.0.2.11 255.255.255.0"
#         - "interface GigabitEthernet0/0/0/1"
#         - " description 'GigabitEthernet - 1""
#         - " bundle id 10 mode inherit"
#         - "interface GigabitEthernet0/0/0/2"
#         - " description "GigabitEthernet - 2""
#         - "  bundle id 12 mode passive"
#         - "interface GigabitEthernet0/0/0/3"
#         - " description "GigabitEthernet - 3""
#         - " bundle id 10 mode inherit"
#         - "interface GigabitEthernet0/0/0/4"
#         - " description "GigabitEthernet - 4""
#         - " bundle id 12 mode passive"
#    ]
#
#


"""
RETURN = """
before:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: list
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
after:
  description: The configuration as structured data after module completion.
  returned: when changed
  type: list
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample: ['interface Bundle-Ether10', 'bundle minimum-active links 2', 'bundle load-balancing hash src-ip']
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.iosxr.plugins.module_utils.network.iosxr.argspec.lag_interfaces.lag_interfaces import (
    Lag_interfacesArgs,
)
from ansible_collections.cisco.iosxr.plugins.module_utils.network.iosxr.config.lag_interfaces.lag_interfaces import (
    Lag_interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    required_if = [
        ("state", "merged", ("config",)),
        ("state", "replaced", ("config",)),
        ("state", "overridden", ("config",)),
        ("state", "rendered", ("config",)),
        ("state", "parsed", ("running_config",)),
    ]

    mutually_exclusive = [("config", "running_config")]
    module = AnsibleModule(
        argument_spec=Lag_interfacesArgs.argument_spec,
        required_if=required_if,
        supports_check_mode=True,
        mutually_exclusive=mutually_exclusive,
    )

    result = Lag_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
