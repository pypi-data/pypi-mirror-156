#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: event_subscription_syslog_info
short_description: Information module for Event Subscription Syslog
description:
- Get all Event Subscription Syslog.
- Gets the list of Syslog Subscriptions's based on provided offset and limit.
version_added: '3.1.0'
extends_documentation_fragment:
  - cisco.dnac.module_info
author: Rafael Campos (@racampos)
options:
  headers:
    description: Additional headers.
    type: dict
  eventIds:
    description:
    - EventIds query parameter. List of subscriptions related to the respective eventIds (Comma separated event ids).
    type: str
  offset:
    description:
    - Offset query parameter. The number of Subscriptions's to offset in the resultset whose default value 0.
    type: int
  limit:
    description:
    - Limit query parameter. The number of Subscriptions's to limit in the resultset whose default value 10.
    type: int
  sortBy:
    description:
    - SortBy query parameter. SortBy field name.
    type: str
  order:
    description:
    - Order query parameter.
    type: str
requirements:
- dnacentersdk >= 2.4.9
- python >= 3.5
notes:
  - SDK Method used are
    event_management.EventManagement.get_syslog_event_subscriptions,

  - Paths used are
    get /dna/intent/api/v1/event/subscription/syslog,

"""

EXAMPLES = r"""
- name: Get all Event Subscription Syslog
  cisco.dnac.event_subscription_syslog_info:
    dnac_host: "{{dnac_host}}"
    dnac_username: "{{dnac_username}}"
    dnac_password: "{{dnac_password}}"
    dnac_verify: "{{dnac_verify}}"
    dnac_port: "{{dnac_port}}"
    dnac_version: "{{dnac_version}}"
    dnac_debug: "{{dnac_debug}}"
    headers:
      custom: value
    eventIds: string
    offset: 0
    limit: 0
    sortBy: string
    order: string
  register: result

"""

RETURN = r"""
dnac_response:
  description: A dictionary or list with the response returned by the Cisco DNAC Python SDK
  returned: always
  type: list
  elements: dict
  sample: >
    [
      {
        "version": "string",
        "subscriptionId": "string",
        "name": "string",
        "description": "string",
        "subscriptionEndpoints": [
          {
            "instanceId": "string",
            "subscriptionDetails": {
              "connectorType": "string",
              "instanceId": "string",
              "name": "string",
              "description": "string",
              "syslogConfig": {
                "version": "string",
                "tenantId": "string",
                "configId": "string",
                "name": "string",
                "description": "string",
                "host": "string",
                "port": "string"
              }
            },
            "connectorType": "string"
          }
        ],
        "filter": {
          "eventIds": [
            "string"
          ],
          "others": [
            "string"
          ],
          "domainsSubdomains": [
            "string"
          ],
          "types": [
            "string"
          ],
          "categories": [
            "string"
          ],
          "severities": [
            {}
          ],
          "sources": [
            "string"
          ]
        },
        "isPrivate": true,
        "tenantId": "string"
      }
    ]
"""
