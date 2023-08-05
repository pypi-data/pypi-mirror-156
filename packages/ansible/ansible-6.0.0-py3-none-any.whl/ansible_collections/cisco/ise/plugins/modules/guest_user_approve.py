#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: guest_user_approve
short_description: Resource module for Guest User Approve
description:
- Manage operation update of the resource Guest User Approve.
- This API allows the client to approve a guest user by ID.
version_added: '1.0.0'
extends_documentation_fragment:
  - cisco.ise.module
author: Rafael Campos (@racampos)
options:
  id:
    description: Id path parameter.
    type: str
requirements:
- ciscoisesdk >= 2.0.1
- python >= 3.5
notes:
  - SDK Method used are
    guest_user.GuestUser.approve_guest_user_by_id,

  - Paths used are
    put /ers/config/guestuser/approve/{id},

"""

EXAMPLES = r"""
- name: Update by id
  cisco.ise.guest_user_approve:
    ise_hostname: "{{ise_hostname}}"
    ise_username: "{{ise_username}}"
    ise_password: "{{ise_password}}"
    ise_verify: "{{ise_verify}}"
    id: string

"""

RETURN = r"""
ise_response:
  description: A dictionary or list with the response returned by the Cisco ISE Python SDK
  returned: always
  type: dict
  sample: >
    {}
"""
