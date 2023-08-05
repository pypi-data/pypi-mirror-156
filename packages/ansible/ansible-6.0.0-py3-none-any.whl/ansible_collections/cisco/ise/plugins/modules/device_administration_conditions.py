#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: device_administration_conditions
short_description: Resource module for Device Administration Conditions
description:
- Manage operations create, update and delete of the resource Device Administration Conditions.
- Device Admin - Creates a library condition.
- Device Admin - Delete a library condition.
- NDevice Admin - Delete a library condition using condition Name.
- Device Admin - Update library condition using condition name.
- Device Admin - Update library condition.
version_added: '1.0.0'
extends_documentation_fragment:
  - cisco.ise.module
author: Rafael Campos (@racampos)
options:
  attributeName:
    description: Dictionary attribute name.
    type: str
  attributeValue:
    description: <ul><li>Attribute value for condition</li> <li>Value type is specified
      in dictionary object</li> <li>if multiple values allowed is specified in dictionary
      object</li></ul>.
    type: str
  children:
    description: In case type is andBlock or orBlock addtional conditions will be aggregated
      under this logical (OR/AND) condition.
    elements: dict
    suboptions:
      conditionType:
        description: <ul><li>Inidicates whether the record is the condition itself(data)
          or a logical(or,and) aggregation</li> <li>Data type enum(reference,single)
          indicates than "conditonId" OR "ConditionAttrs" fields should contain condition
          data but not both</li> <li>Logical aggreation(and,or) enum indicates that
          additional conditions are present under the children field</li></ul>.
        type: str
      isNegate:
        description: Indicates whereas this condition is in negate mode.
        type: bool
      link:
        description: Device Administration Conditions's link.
        suboptions:
          href:
            description: Device Administration Conditions's href.
            type: str
          rel:
            description: Device Administration Conditions's rel.
            type: str
          type:
            description: Device Administration Conditions's type.
            type: str
        type: dict
    type: list
  conditionType:
    description: <ul><li>Inidicates whether the record is the condition itself(data)
      or a logical(or,and) aggregation</li> <li>Data type enum(reference,single) indicates
      than "conditonId" OR "ConditionAttrs" fields should contain condition data but
      not both</li> <li>Logical aggreation(and,or) enum indicates that additional conditions
      are present under the children field</li></ul>.
    type: str
  datesRange:
    description: <p>Defines for which date/s TimeAndDate condition will be matched<br>
      Options are - Date range, for specific date, the same date should be used for
      start/end date <br> Default - no specific dates<br> In order to reset the dates
      to have no specific dates Date format - yyyy-mm-dd (MM = month, dd = day, yyyy
      = year)</p>.
    suboptions:
      endDate:
        description: Device Administration Conditions's endDate.
        type: str
      startDate:
        description: Device Administration Conditions's startDate.
        type: str
    type: dict
  datesRangeException:
    description: <p>Defines for which date/s TimeAndDate condition will be matched<br>
      Options are - Date range, for specific date, the same date should be used for
      start/end date <br> Default - no specific dates<br> In order to reset the dates
      to have no specific dates Date format - yyyy-mm-dd (MM = month, dd = day, yyyy
      = year)</p>.
    suboptions:
      endDate:
        description: Device Administration Conditions's endDate.
        type: str
      startDate:
        description: Device Administration Conditions's startDate.
        type: str
    type: dict
  description:
    description: Condition description.
    type: str
  dictionaryName:
    description: Dictionary name.
    type: str
  dictionaryValue:
    description: Dictionary value.
    type: str
  hoursRange:
    description: <p>Defines for which hours a TimeAndDate condition will be matched<br>
      Time format - hh mm ( h = hour , mm = minutes ) <br> Default - All Day </p>.
    suboptions:
      endTime:
        description: Device Administration Conditions's endTime.
        type: str
      startTime:
        description: Device Administration Conditions's startTime.
        type: str
    type: dict
  hoursRangeException:
    description: <p>Defines for which hours a TimeAndDate condition will be matched<br>
      Time format - hh mm ( h = hour , mm = minutes ) <br> Default - All Day </p>.
    suboptions:
      endTime:
        description: Device Administration Conditions's endTime.
        type: str
      startTime:
        description: Device Administration Conditions's startTime.
        type: str
    type: dict
  id:
    description: Device Administration Conditions's id.
    type: str
  isNegate:
    description: Indicates whereas this condition is in negate mode.
    type: bool
  link:
    description: Device Administration Conditions's link.
    suboptions:
      href:
        description: Device Administration Conditions's href.
        type: str
      rel:
        description: Device Administration Conditions's rel.
        type: str
      type:
        description: Device Administration Conditions's type.
        type: str
    type: dict
  name:
    description: Condition name.
    type: str
  operator:
    description: Equality operator.
    type: str
  weekDays:
    description: <p>Defines for which days this condition will be matched<br> Days format
      - Arrays of WeekDay enums <br> Default - List of All week days</p>.
    elements: str
    type: list
  weekDaysException:
    description: <p>Defines for which days this condition will NOT be matched<br> Days
      format - Arrays of WeekDay enums <br> Default - Not enabled</p>.
    elements: str
    type: list
requirements:
- ciscoisesdk >= 2.0.1
- python >= 3.5
seealso:
- name: Cisco ISE documentation for Device Administration - Conditions
  description: Complete reference of the Device Administration - Conditions API.
  link: https://developer.cisco.com/docs/identity-services-engine/v1/#!policy-openapi
notes:
  - SDK Method used are
    device_administration_conditions.DeviceAdministrationConditions.create_device_admin_condition,
    device_administration_conditions.DeviceAdministrationConditions.delete_device_admin_condition_by_id,
    device_administration_conditions.DeviceAdministrationConditions.delete_device_admin_condition_by_name,
    device_administration_conditions.DeviceAdministrationConditions.update_device_admin_condition_by_id,
    device_administration_conditions.DeviceAdministrationConditions.update_device_admin_condition_by_name,

  - Paths used are
    post /device-admin/condition,
    delete /device-admin/condition/condition-by-name/{name},
    delete /device-admin/condition/{id},
    put /device-admin/condition/condition-by-name/{name},
    put /device-admin/condition/{id},

"""

EXAMPLES = r"""
- name: Create
  cisco.ise.device_administration_conditions:
    ise_hostname: "{{ise_hostname}}"
    ise_username: "{{ise_username}}"
    ise_password: "{{ise_password}}"
    ise_verify: "{{ise_verify}}"
    state: present
    attributeName: string
    attributeValue: string
    children:
    - conditionType: string
      isNegate: true
      link:
        href: string
        rel: string
        type: string
    conditionType: string
    datesRange:
      endDate: string
      startDate: string
    datesRangeException:
      endDate: string
      startDate: string
    description: string
    dictionaryName: string
    dictionaryValue: string
    hoursRange:
      endTime: string
      startTime: string
    hoursRangeException:
      endTime: string
      startTime: string
    id: string
    isNegate: true
    link:
      href: string
      rel: string
      type: string
    name: string
    operator: string
    weekDays:
    - string
    weekDaysException:
    - string

- name: Update by name
  cisco.ise.device_administration_conditions:
    ise_hostname: "{{ise_hostname}}"
    ise_username: "{{ise_username}}"
    ise_password: "{{ise_password}}"
    ise_verify: "{{ise_verify}}"
    state: present
    attributeName: string
    attributeValue: string
    children:
    - conditionType: string
      isNegate: true
      link:
        href: string
        rel: string
        type: string
    conditionType: string
    datesRange:
      endDate: string
      startDate: string
    datesRangeException:
      endDate: string
      startDate: string
    description: string
    dictionaryName: string
    dictionaryValue: string
    hoursRange:
      endTime: string
      startTime: string
    hoursRangeException:
      endTime: string
      startTime: string
    id: string
    isNegate: true
    link:
      href: string
      rel: string
      type: string
    name: string
    operator: string
    weekDays:
    - string
    weekDaysException:
    - string

- name: Delete by name
  cisco.ise.device_administration_conditions:
    ise_hostname: "{{ise_hostname}}"
    ise_username: "{{ise_username}}"
    ise_password: "{{ise_password}}"
    ise_verify: "{{ise_verify}}"
    state: absent
    name: string

- name: Update by id
  cisco.ise.device_administration_conditions:
    ise_hostname: "{{ise_hostname}}"
    ise_username: "{{ise_username}}"
    ise_password: "{{ise_password}}"
    ise_verify: "{{ise_verify}}"
    state: present
    attributeName: string
    attributeValue: string
    children:
    - conditionType: string
      isNegate: true
      link:
        href: string
        rel: string
        type: string
    conditionType: string
    datesRange:
      endDate: string
      startDate: string
    datesRangeException:
      endDate: string
      startDate: string
    description: string
    dictionaryName: string
    dictionaryValue: string
    hoursRange:
      endTime: string
      startTime: string
    hoursRangeException:
      endTime: string
      startTime: string
    id: string
    isNegate: true
    link:
      href: string
      rel: string
      type: string
    name: string
    operator: string
    weekDays:
    - string
    weekDaysException:
    - string

- name: Delete by id
  cisco.ise.device_administration_conditions:
    ise_hostname: "{{ise_hostname}}"
    ise_username: "{{ise_username}}"
    ise_password: "{{ise_password}}"
    ise_verify: "{{ise_verify}}"
    state: absent
    id: string

"""

RETURN = r"""
ise_response:
  description: A dictionary or list with the response returned by the Cisco ISE Python SDK
  returned: always
  type: dict
  sample: >
    {
      "conditionType": "string",
      "isNegate": true,
      "link": {
        "href": "string",
        "rel": "string",
        "type": "string"
      },
      "description": "string",
      "id": "string",
      "name": "string",
      "attributeName": "string",
      "attributeValue": "string",
      "dictionaryName": "string",
      "dictionaryValue": "string",
      "operator": "string",
      "children": [
        {
          "conditionType": "string",
          "isNegate": true,
          "link": {
            "href": "string",
            "rel": "string",
            "type": "string"
          }
        }
      ],
      "datesRange": {
        "endDate": "string",
        "startDate": "string"
      },
      "datesRangeException": {
        "endDate": "string",
        "startDate": "string"
      },
      "hoursRange": {
        "endTime": "string",
        "startTime": "string"
      },
      "hoursRangeException": {
        "endTime": "string",
        "startTime": "string"
      },
      "weekDays": [
        "string"
      ],
      "weekDaysException": [
        "string"
      ]
    }

ise_update_response:
  description: A dictionary or list with the response returned by the Cisco ISE Python SDK
  returned: always
  version_added: '1.1.0'
  type: dict
  sample: >
    {
      "response": {
        "conditionType": "string",
        "isNegate": true,
        "link": {
          "href": "string",
          "rel": "string",
          "type": "string"
        },
        "description": "string",
        "id": "string",
        "name": "string",
        "attributeName": "string",
        "attributeValue": "string",
        "dictionaryName": "string",
        "dictionaryValue": "string",
        "operator": "string",
        "children": [
          {
            "conditionType": "string",
            "isNegate": true,
            "link": {
              "href": "string",
              "rel": "string",
              "type": "string"
            }
          }
        ],
        "datesRange": {
          "endDate": "string",
          "startDate": "string"
        },
        "datesRangeException": {
          "endDate": "string",
          "startDate": "string"
        },
        "hoursRange": {
          "endTime": "string",
          "startTime": "string"
        },
        "hoursRangeException": {
          "endTime": "string",
          "startTime": "string"
        },
        "weekDays": [
          "string"
        ],
        "weekDaysException": [
          "string"
        ]
      },
      "version": "string"
    }
"""
