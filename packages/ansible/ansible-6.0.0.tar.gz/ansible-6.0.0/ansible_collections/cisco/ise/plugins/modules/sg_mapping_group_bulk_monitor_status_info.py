#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: sg_mapping_group_bulk_monitor_status_info
short_description: Information module for SG Mapping Group Bulk Monitor Status
description:
- Get SG Mapping Group Bulk Monitor Status by id.
- This API allows the client to monitor the bulk request.
version_added: '1.0.0'
extends_documentation_fragment:
  - cisco.ise.module_info
author: Rafael Campos (@racampos)
options:
  bulkid:
    description:
    - Bulkid path parameter.
    type: str
requirements:
- ciscoisesdk >= 2.0.1
- python >= 3.5
seealso:
- name: Cisco ISE documentation for IPToSGTMappingGroup
  description: Complete reference of the IPToSGTMappingGroup API.
  link: https://developer.cisco.com/docs/identity-services-engine/v1/#!sgmappinggroup
notes:
  - SDK Method used are
    ip_to_sgt_mapping_group.IpToSgtMappingGroup.monitor_bulk_status_ip_to_sgt_mapping_group,

  - Paths used are
    get /ers/config/sgmappinggroup/bulk/{bulkid},

"""

EXAMPLES = r"""
- name: Get SG Mapping Group Bulk Monitor Status by id
  cisco.ise.sg_mapping_group_bulk_monitor_status_info:
    ise_hostname: "{{ise_hostname}}"
    ise_username: "{{ise_username}}"
    ise_password: "{{ise_password}}"
    ise_verify: "{{ise_verify}}"
    bulkid: string
  register: result

"""

RETURN = r"""
ise_response:
  description: A dictionary or list with the response returned by the Cisco ISE Python SDK
  returned: always
  type: dict
  sample: >
    {
      "bulkId": "string",
      "mediaType": "string",
      "executionStatus": "string",
      "operationType": "string",
      "startTime": "string",
      "resourcesCount": 0,
      "successCount": 0,
      "failCount": 0,
      "resourcesStatus": [
        {
          "id": "string",
          "name": "string",
          "description": "string",
          "resourceExecutionStatus": "string",
          "status": "string"
        }
      ]
    }
"""
