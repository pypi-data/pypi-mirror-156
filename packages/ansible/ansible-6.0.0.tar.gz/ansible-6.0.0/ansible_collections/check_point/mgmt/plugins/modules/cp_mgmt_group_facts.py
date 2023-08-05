#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Check Point Firewall (c) 2019
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: cp_mgmt_group_facts
short_description: Get group objects facts on Check Point over Web Services API
description:
  - Get group objects facts on Check Point devices.
  - All operations are performed over Web Services API.
  - This module handles both operations, get a specific object and get several objects,
    For getting a specific object use the parameter 'name'.
version_added: "2.9"
author: "Or Soffer (@chkp-orso)"
options:
  name:
    description:
      - Object name.
        This parameter is relevant only for getting a specific object.
    type: str
  show_as_ranges:
    description:
      - When true, the group's matched content is displayed as ranges of IP addresses rather than network objects.<br />Objects that are not
        represented using IP addresses are presented as objects.<br />The 'members' parameter is omitted from the response and instead the 'ranges' parameter
        is displayed.
    type: bool
  details_level:
    description:
      - The level of detail for some of the fields in the response can vary from showing only the UID value of the object to a fully detailed
        representation of the object.
    type: str
    choices: ['uid', 'standard', 'full']
  limit:
    description:
      - No more than that many results will be returned.
        This parameter is relevant only for getting few objects.
    type: int
  offset:
    description:
      - Skip that many results before beginning to return them.
        This parameter is relevant only for getting few objects.
    type: int
  order:
    description:
      - Sorts results by the given field. By default the results are sorted in the ascending order by name.
        This parameter is relevant only for getting few objects.
    type: list
    suboptions:
      ASC:
        description:
          - Sorts results by the given field in ascending order.
        type: str
        choices: ['name']
      DESC:
        description:
          - Sorts results by the given field in descending order.
        type: str
        choices: ['name']
  dereference_group_members:
    description:
      - Indicates whether to dereference "members" field by details level for every object in reply.
    type: bool
  show_membership:
    description:
      - Indicates whether to calculate and show "groups" field for every object in reply.
    type: bool
extends_documentation_fragment: check_point.mgmt.checkpoint_facts
"""

EXAMPLES = """
- name: show-group
  cp_mgmt_group_facts:
    name: Demo_Group

- name: show-groups
  cp_mgmt_group_facts:
    details_level: standard
    limit: 50
    offset: 0
"""

RETURN = """
ansible_facts:
  description: The checkpoint object facts.
  returned: always.
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.check_point.mgmt.plugins.module_utils.checkpoint import checkpoint_argument_spec_for_facts, api_call_facts


def main():
    argument_spec = dict(
        name=dict(type='str'),
        show_as_ranges=dict(type='bool'),
        details_level=dict(type='str', choices=['uid', 'standard', 'full']),
        limit=dict(type='int'),
        offset=dict(type='int'),
        order=dict(type='list', options=dict(
            ASC=dict(type='str', choices=['name']),
            DESC=dict(type='str', choices=['name'])
        )),
        dereference_group_members=dict(type='bool'),
        show_membership=dict(type='bool')
    )
    argument_spec.update(checkpoint_argument_spec_for_facts)

    module = AnsibleModule(argument_spec=argument_spec)

    api_call_object = "group"
    api_call_object_plural_version = "groups"

    result = api_call_facts(module, api_call_object, api_call_object_plural_version)
    module.exit_json(ansible_facts=result)


if __name__ == '__main__':
    main()
