#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: mso_schema_template_anp
short_description: Manage Application Network Profiles (ANPs) in schema templates
description:
- Manage ANPs in schema templates on Cisco ACI Multi-Site.
author:
- Dag Wieers (@dagwieers)
options:
  schema:
    description:
    - The name of the schema.
    type: str
    required: yes
  template:
    description:
    - The name of the template.
    type: str
    required: yes
  anp:
    description:
    - The name of the ANP to manage.
    type: str
    aliases: [ name ]
  description:
    description:
    - The description of ANP is supported on versions of MSO that are 3.3 or greater.
    type: str
  display_name:
    description:
    - The name as displayed on the MSO web interface.
    type: str
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, present, query ]
    default: present
seealso:
- module: cisco.mso.mso_schema_template
- module: cisco.mso.mso_schema_template_anp_epg
extends_documentation_fragment: cisco.mso.modules
'''

EXAMPLES = r'''
- name: Add a new ANP
  cisco.mso.mso_schema_template_anp:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    anp: ANP 1
    state: present
  delegate_to: localhost

- name: Remove an ANP
  cisco.mso.mso_schema_template_anp:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    anp: ANP 1
    state: absent
  delegate_to: localhost

- name: Query a specific ANPs
  cisco.mso.mso_schema_template_anp:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    state: query
  delegate_to: localhost
  register: query_result

- name: Query all ANPs
  cisco.mso.mso_schema_template_anp:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    state: query
  delegate_to: localhost
  register: query_result
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.mso.plugins.module_utils.mso import MSOModule, mso_argument_spec


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        schema=dict(type='str', required=True),
        template=dict(type='str', required=True),
        anp=dict(type='str', aliases=['name']),  # This parameter is not required for querying all objects
        description=dict(type='str'),
        display_name=dict(type='str'),
        state=dict(type='str', default='present', choices=['absent', 'present', 'query']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'absent', ['anp']],
            ['state', 'present', ['anp']],
        ],
    )

    schema = module.params.get('schema')
    template = module.params.get('template').replace(' ', '')
    anp = module.params.get('anp')
    description = module.params.get('description')
    display_name = module.params.get('display_name')
    state = module.params.get('state')

    mso = MSOModule(module)

    # Get schema
    schema_id, schema_path, schema_obj = mso.query_schema(schema)

    # Get template
    templates = [t.get('name') for t in schema_obj.get('templates')]
    if template not in templates:
        mso.fail_json(msg="Provided template '{0}' does not exist. Existing templates: {1}".format(template, ', '.join(templates)))
    template_idx = templates.index(template)

    # Get ANP
    anps = [a.get('name') for a in schema_obj.get('templates')[template_idx]['anps']]

    if anp is not None and anp in anps:
        anp_idx = anps.index(anp)
        mso.existing = schema_obj.get('templates')[template_idx]['anps'][anp_idx]

    if state == 'query':
        if anp is None:
            mso.existing = schema_obj.get('templates')[template_idx]['anps']
        elif not mso.existing:
            mso.fail_json(msg="ANP '{anp}' not found".format(anp=anp))
        mso.exit_json()

    anps_path = '/templates/{0}/anps'.format(template)
    anp_path = '/templates/{0}/anps/{1}'.format(template, anp)
    ops = []

    mso.previous = mso.existing
    if state == 'absent':
        if mso.existing:
            mso.sent = mso.existing = {}
            ops.append(dict(op='remove', path=anp_path))

    elif state == 'present':

        if display_name is None and not mso.existing:
            display_name = anp

        epgs = []
        if mso.existing:
            epgs = None

        payload = dict(
            name=anp,
            displayName=display_name,
            epgs=epgs,
        )

        if description is not None:
            payload.update(description=description)

        mso.sanitize(payload, collate=True)

        if mso.existing:
            if display_name is not None:
                ops.append(dict(op='replace', path=anp_path + '/displayName', value=display_name))
        else:
            ops.append(dict(op='add', path=anps_path + '/-', value=mso.sent))

        mso.existing = mso.proposed

    if 'anpRef' in mso.previous:
        del mso.previous['anpRef']

    if not module.check_mode:
        mso.request(schema_path, method='PATCH', data=ops)

    mso.exit_json()


if __name__ == "__main__":
    main()
