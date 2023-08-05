#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: network_device_equipment_info
short_description: Information module for Network Device Equipment
description:
- Get all Network Device Equipment.
- Return PowerSupply/ Fan details for the Given device.
version_added: '3.1.0'
extends_documentation_fragment:
  - cisco.dnac.module_info
author: Rafael Campos (@racampos)
options:
  headers:
    description: Additional headers.
    type: dict
  deviceUuid:
    description:
    - DeviceUuid path parameter.
    type: str
  type:
    description:
    - Type query parameter. Type value should be PowerSupply or Fan.
    type: str
requirements:
- dnacentersdk >= 2.4.9
- python >= 3.5
notes:
  - SDK Method used are
    devices.Devices.return_power_supply_fan_details_for_the_given_device,

  - Paths used are
    get /dna/intent/api/v1/network-device/{deviceUuid}/equipment,

"""

EXAMPLES = r"""
- name: Get all Network Device Equipment
  cisco.dnac.network_device_equipment_info:
    dnac_host: "{{dnac_host}}"
    dnac_username: "{{dnac_username}}"
    dnac_password: "{{dnac_password}}"
    dnac_verify: "{{dnac_verify}}"
    dnac_port: "{{dnac_port}}"
    dnac_version: "{{dnac_version}}"
    dnac_debug: "{{dnac_debug}}"
    headers:
      custom: value
    type: string
    deviceUuid: string
  register: result

"""

RETURN = r"""
dnac_response:
  description: A dictionary or list with the response returned by the Cisco DNAC Python SDK
  returned: always
  type: dict
  sample: >
    {
      "response": [
        {
          "operationalStateCode": "string",
          "productId": "string",
          "serialNumber": "string",
          "vendorEquipmentType": "string",
          "description": "string",
          "instanceUuid": "string",
          "name": "string"
        }
      ],
      "version": "string"
    }
"""
