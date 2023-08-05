#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = r'''
---
module: aci_vmm_uplink
short_description: Manage VMM uplinks (vmm:UplinkP)
description:
- Manage VMM Uplinks on Cisco ACI fabrics.
options:
  domain:
    description:
    - Name of the VMM domain
    type: str
  uplink_id:
    description:
    - Numerical ID of the uplink
    type: int
  uplink_name:
    description:
    - Name of the uplink
    type: str
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, present, query ]
    default: present
extends_documentation_fragment:
- cisco.aci.aci

notes:
- The C(domain) used must exist before using this module in your playbook.
  The M(cisco.aci.aci_domain) module can be used for this.
seealso:
- module: cisco.aci.aci_domain
- module: cisco.aci.aci_vmm_uplink_container
- name: APIC Management Information Model reference
  description: More information about the internal APIC class B(vmm:UplinkP).
  link: https://developer.cisco.com/docs/apic-mim-ref/
author:
- Tim Cragg (@timcragg)
'''

EXAMPLES = r'''
- name: Add a new uplink
  cisco.aci.aci_vmm_uplink:
    host: apic
    username: admin
    password: SomeSecretPassword
    domain: my_vmm_domain
    uplink_id: 1
    uplink_name: uplink1
    state: present
  delegate_to: localhost

- name: Delete uplink container
  cisco.aci.aci_vmm_uplink:
    host: apic
    username: admin
    password: SomeSecretPassword
    domain: my_vmm_domain
    uplink_id: 1
    state: absent
  delegate_to: localhost

- name: Query uplink container
  cisco.aci.aci_vmm_uplink_container:
    host: apic
    username: admin
    password: SomeSecretPassword
    domain: my_vmm_domain
    state: query
  delegate_to: localhost
  register: query_result
'''

RETURN = r'''
current:
  description: The existing configuration from the APIC after the module has finished
  returned: success
  type: list
  sample:
    [
        {
            "fvTenant": {
                "attributes": {
                    "descr": "Production environment",
                    "dn": "uni/tn-production",
                    "name": "production",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": ""
                }
            }
        }
    ]
error:
  description: The error information as returned from the APIC
  returned: failure
  type: dict
  sample:
    {
        "code": "122",
        "text": "unknown managed object class foo"
    }
raw:
  description: The raw output returned by the APIC REST API (xml or json)
  returned: parse error
  type: str
  sample: '<?xml version="1.0" encoding="UTF-8"?><imdata totalCount="1"><error code="122" text="unknown managed object class foo"/></imdata>'
sent:
  description: The actual/minimal configuration pushed to the APIC
  returned: info
  type: list
  sample:
    {
        "fvTenant": {
            "attributes": {
                "descr": "Production environment"
            }
        }
    }
previous:
  description: The original configuration from the APIC before the module has started
  returned: info
  type: list
  sample:
    [
        {
            "fvTenant": {
                "attributes": {
                    "descr": "Production",
                    "dn": "uni/tn-production",
                    "name": "production",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": ""
                }
            }
        }
    ]
proposed:
  description: The assembled configuration from the user-provided parameters
  returned: info
  type: dict
  sample:
    {
        "fvTenant": {
            "attributes": {
                "descr": "Production environment",
                "name": "production"
            }
        }
    }
filter_string:
  description: The filter string used for the request
  returned: failure or debug
  type: str
  sample: ?rsp-prop-include=config-only
method:
  description: The HTTP method used for the request to the APIC
  returned: failure or debug
  type: str
  sample: POST
response:
  description: The HTTP response from the APIC
  returned: failure or debug
  type: str
  sample: OK (30 bytes)
status:
  description: The HTTP status from the APIC
  returned: failure or debug
  type: int
  sample: 200
url:
  description: The HTTP url used for the request to the APIC
  returned: failure or debug
  type: str
  sample: https://10.11.12.13/api/mo/uni/tn-production.json
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.aci.plugins.module_utils.aci import ACIModule, aci_argument_spec


def main():
    argument_spec = aci_argument_spec()
    argument_spec.update(
        domain=dict(type='str'),
        uplink_id=dict(type='int'),
        uplink_name=dict(type='str'),
        state=dict(type='str', default='present', choices=['absent', 'present', 'query']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'absent', ['uplink_id', 'domain']],
            ['state', 'present', ['uplink_id', 'domain']],
        ],
    )

    domain = module.params.get('domain')
    uplink_id = module.params.get('uplink_id')
    uplink_name = module.params.get('uplink_name')
    state = module.params.get('state')

    aci = ACIModule(module)

    aci.construct_url(
        root_class=dict(
            aci_class='vmmProvP',
            aci_rn='vmmp-VMware',
            module_object='VMware',
            target_filter={'name': 'VMware'},
        ),
        subclass_1=dict(
            aci_class='vmmDomP',
            aci_rn='dom-{0}'.format(domain),
            module_object=domain,
            target_filter={'name': domain},
        ),
        subclass_2=dict(
            aci_class='vmmUplinkPCont',
            aci_rn='uplinkpcont',
            module_object='uplinkpcont',
            target_filter={'rn': 'uplinkpcont'},
        ),
        subclass_3=dict(
            aci_class='vmmUplinkP',
            aci_rn='uplinkp-{0}'.format(uplink_id),
            module_object=uplink_id,
            target_filter={'uplinkId': uplink_id},
        ),
    )

    aci.get_existing()

    if state == 'present':
        aci.payload(
            aci_class='vmmUplinkP',
            class_config=dict(
                uplinkId=uplink_id,
                uplinkName=uplink_name,
            ),
        )

        aci.get_diff(aci_class='vmmUplinkP')

        aci.post_config()

    elif state == 'absent':
        aci.delete_config()

    aci.exit_json()


if __name__ == "__main__":
    main()
