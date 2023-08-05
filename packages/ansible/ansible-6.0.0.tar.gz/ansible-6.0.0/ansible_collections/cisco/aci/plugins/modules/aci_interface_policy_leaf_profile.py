#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Bruno Calogero <brunocalogero@hotmail.com>
# Copyright: (c) 2020, Shreyas Srish <ssrish@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "certified"}

DOCUMENTATION = r"""
---
module: aci_interface_policy_leaf_profile
short_description: Manage fabric interface policy leaf profiles (infra:AccPortP)
description:
- Manage fabric interface policy leaf profiles on Cisco ACI fabrics.
options:
  interface_profile:
    description:
    - The name of the Fabric access policy leaf interface profile.
    type: str
    aliases: [ name, leaf_interface_profile_name, leaf_interface_profile, interface_profile_name ]
  description:
    description:
    - Description for the Fabric access policy leaf interface profile.
    type: str
    aliases: [ descr ]
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, present, query ]
    default: present
  name_alias:
    description:
    - The alias for the current object. This relates to the nameAlias field in ACI.
    type: str
  type:
    description:
    - The type of profile to be created.
    type: str
    choices: [ fex, leaf ]
    default: leaf
extends_documentation_fragment:
- cisco.aci.aci
- cisco.aci.annotation
- cisco.aci.owner

seealso:
- name: APIC Management Information Model reference
  description: More information about the internal APIC class B(infra:AccPortP).
  link: https://developer.cisco.com/docs/apic-mim-ref/
author:
- Bruno Calogero (@brunocalogero)
- Shreyas Srish (@shrsr)
"""

EXAMPLES = r"""
- name: Add a new leaf_interface_profile
  cisco.aci.aci_interface_policy_leaf_profile:
    host: apic
    username: admin
    password: SomeSecretPassword
    interface_profile: leafintprfname
    description:  leafintprfname description
    state: present
  delegate_to: localhost

- name: Add a new leaf_interface_profile of type fex
  cisco.aci.aci_interface_policy_leaf_profile:
    host: apic
    username: admin
    password: SomeSecretPassword
    interface_profile: leafintprfname_fex
    type: fex
    description: leafintprfname description
    state: present
  delegate_to: localhost

- name: Remove a leaf_interface_profile
  cisco.aci.aci_interface_policy_leaf_profile:
    host: apic
    username: admin
    password: SomeSecretPassword
    interface_profile: leafintprfname
    state: absent
  delegate_to: localhost

- name: Remove a leaf_interface_profile of type fex
  cisco.aci.aci_interface_policy_leaf_profile:
    host: apic
    username: admin
    password: SomeSecretPassword
    interface_profile: leafintprfname_fex
    type: fex
    state: absent
  delegate_to: localhost

- name: Query a leaf_interface_profile
  cisco.aci.aci_interface_policy_leaf_profile:
    host: apic
    username: admin
    password: SomeSecretPassword
    interface_profile: leafintprfname
    state: query
  delegate_to: localhost
  register: query_result

- name: Query a leaf_interface_profile of type fex
  cisco.aci.aci_interface_policy_leaf_profile:
    host: apic
    username: admin
    password: SomeSecretPassword
    interface_profile: leafintprfname_fex
    type: fex
    state: query
  delegate_to: localhost
  register: query_result

- name: Query all leaf_interface_profiles
  cisco.aci.aci_interface_policy_leaf_profile:
    host: apic
    username: admin
    password: SomeSecretPassword
    state: query
  delegate_to: localhost

- name: Query all leaf_interface_profiles of type fex
  cisco.aci.aci_interface_policy_leaf_profile:
    host: apic
    username: admin
    password: SomeSecretPassword
    type: fex
    state: query
  delegate_to: localhost
"""

RETURN = r"""
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
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.aci.plugins.module_utils.aci import ACIModule, aci_argument_spec, aci_annotation_spec, aci_owner_spec


def main():
    argument_spec = aci_argument_spec()
    argument_spec.update(aci_annotation_spec())
    argument_spec.update(aci_owner_spec())
    argument_spec.update(
        interface_profile=dict(type="str", aliases=["name", "leaf_interface_profile_name", "leaf_interface_profile", "interface_profile_name"]),
        description=dict(type="str", aliases=["descr"]),
        state=dict(type="str", default="present", choices=["absent", "present", "query"]),
        name_alias=dict(type="str"),
        type=dict(type="str", default="leaf", choices=["fex", "leaf"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "absent", ["interface_profile"]],
            ["state", "present", ["interface_profile"]],
        ],
    )

    interface_profile = module.params.get("interface_profile")
    description = module.params.get("description")
    state = module.params.get("state")
    name_alias = module.params.get("name_alias")
    type_profile = module.params.get("type")

    aci = ACIModule(module)
    aci_class = "infraAccPortP"
    aci_rn = "accportprof"
    if type_profile == "fex":
        aci_class = "infraFexP"
        aci_rn = "fexprof"
    aci.construct_url(
        root_class=dict(
            aci_class=aci_class,
            aci_rn="infra/" + aci_rn + "-{0}".format(interface_profile),
            module_object=interface_profile,
            target_filter={"name": interface_profile},
        ),
    )

    aci.get_existing()

    if state == "present":
        aci.payload(
            aci_class=aci_class,
            class_config=dict(
                name=interface_profile,
                descr=description,
                nameAlias=name_alias,
            ),
        )

        aci.get_diff(aci_class=aci_class)

        aci.post_config()

    elif state == "absent":
        aci.delete_config()

    aci.exit_json()


if __name__ == "__main__":
    main()
