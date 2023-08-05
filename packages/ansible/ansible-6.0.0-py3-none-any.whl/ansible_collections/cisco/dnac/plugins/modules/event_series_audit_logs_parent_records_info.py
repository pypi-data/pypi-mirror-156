#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: event_series_audit_logs_parent_records_info
short_description: Information module for Event Series Audit Logs Parent Records
description:
- Get all Event Series Audit Logs Parent Records.
- Get Parent Audit Log Event instances from the Event-Hub.
version_added: '3.1.0'
extends_documentation_fragment:
  - cisco.dnac.module_info
author: Rafael Campos (@racampos)
options:
  headers:
    description: Additional headers.
    type: dict
  instanceId:
    description:
    - InstanceId query parameter. InstanceID of the Audit Log.
    type: str
  name:
    description:
    - Name query parameter. Audit Log notification event name.
    type: str
  eventId:
    description:
    - EventId query parameter. Audit Log notification's event ID.
    type: str
  category:
    description:
    - >
      Category query parameter. Audit Log notification's event category. Supported values INFO, WARN, ERROR,
      ALERT, TASK_PROGRESS, TASK_FAILURE, TASK_COMPLETE, COMMAND, QUERY, CONVERSATION.
    type: str
  severity:
    description:
    - Severity query parameter. Audit Log notification's event severity. Supported values 1, 2, 3, 4, 5.
    type: str
  domain:
    description:
    - Domain query parameter. Audit Log notification's event domain.
    type: str
  subDomain:
    description:
    - SubDomain query parameter. Audit Log notification's event sub-domain.
    type: str
  source:
    description:
    - Source query parameter. Audit Log notification's event source.
    type: str
  userId:
    description:
    - UserId query parameter. Audit Log notification's event userId.
    type: str
  context:
    description:
    - Context query parameter. Audit Log notification's event correlationId.
    type: str
  eventHierarchy:
    description:
    - >
      EventHierarchy query parameter. Audit Log notification's event eventHierarchy. Example "US.CA.San Jose" OR
      "US.CA" OR "CA.San Jose" - Delimiter for hierarchy separation is ".".
    type: str
  siteId:
    description:
    - SiteId query parameter. Audit Log notification's siteId.
    type: str
  deviceId:
    description:
    - DeviceId query parameter. Audit Log notification's deviceId.
    type: str
  isSystemEvents:
    description:
    - IsSystemEvents query parameter. Parameter to filter system generated audit-logs.
    type: bool
  description:
    description:
    - >
      Description query parameter. String full/partial search - (Provided input string is case insensitively
      matched for records).
    type: str
  offset:
    description:
    - Offset query parameter. Position of a particular Audit Log record in the data.
    type: int
  limit:
    description:
    - Limit query parameter. Number of Audit Log records to be returned per page.
    type: int
  startTime:
    description:
    - >
      StartTime query parameter. Start Time in milliseconds since Epoch Eg. 1597950637211 (when provided endTime
      is mandatory).
    type: int
  endTime:
    description:
    - >
      EndTime query parameter. End Time in milliseconds since Epoch Eg. 1597961437211 (when provided startTime is
      mandatory).
    type: int
  sortBy:
    description:
    - >
      SortBy query parameter. Sort the Audit Logs by certain fields. Supported values are event notification
      header attributes.
    type: str
  order:
    description:
    - >
      Order query parameter. Order of the sorted Audit Log records. Default value is desc by timestamp. Supported
      values asc, desc.
    type: str
requirements:
- dnacentersdk >= 2.4.9
- python >= 3.5
notes:
  - SDK Method used are
    event_management.EventManagement.get_auditlog_parent_records,

  - Paths used are
    get /dna/data/api/v1/event/event-series/audit-log/parent-records,

"""

EXAMPLES = r"""
- name: Get all Event Series Audit Logs Parent Records
  cisco.dnac.event_series_audit_logs_parent_records_info:
    dnac_host: "{{dnac_host}}"
    dnac_username: "{{dnac_username}}"
    dnac_password: "{{dnac_password}}"
    dnac_verify: "{{dnac_verify}}"
    dnac_port: "{{dnac_port}}"
    dnac_version: "{{dnac_version}}"
    dnac_debug: "{{dnac_debug}}"
    headers:
      custom: value
    instanceId: string
    name: string
    eventId: string
    category: string
    severity: string
    domain: string
    subDomain: string
    source: string
    userId: string
    context: string
    eventHierarchy: string
    siteId: string
    deviceId: string
    isSystemEvents: True
    description: string
    offset: 0
    limit: 0
    startTime: 0
    endTime: 0
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
        "instanceId": "string",
        "eventId": "string",
        "namespace": "string",
        "name": "string",
        "description": "string",
        "type": "string",
        "category": "string",
        "domain": "string",
        "subDomain": "string",
        "severity": 0,
        "source": "string",
        "timestamp": 0,
        "tags": [
          {}
        ],
        "details": {},
        "ciscoDnaEventLink": "string",
        "note": "string",
        "tntId": "string",
        "context": "string",
        "userId": "string",
        "i18n": "string",
        "eventHierarchy": "string",
        "message": "string",
        "messageParams": "string",
        "additionalDetails": {},
        "parentInstanceId": "string",
        "network": "string",
        "childCount": 0,
        "tenantId": "string"
      }
    ]
"""
