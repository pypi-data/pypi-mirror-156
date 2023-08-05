#!/usr/bin/python
# Copyright (c) 2018-2019 Red Hat, Inc.
# Copyright (c) 2020 Infoblox, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_naptr_record
author: "Blair Rampling (@brampling)"
short_description: Configure Infoblox NIOS NAPTR records
version_added: "1.0.0"
description:
  - Adds and/or removes instances of NAPTR record objects from
    Infoblox NIOS servers.  This module manages NIOS C(record:naptr) objects
    using the Infoblox WAPI interface over REST.
requirements:
  - infoblox_client
extends_documentation_fragment: infoblox.nios_modules.nios
notes:
    - This module supports C(check_mode).
options:
  name:
    description:
      - Specifies the fully qualified hostname to add or remove from
        the system.
    type: str
    required: true
  view:
    description:
      - Sets the DNS view to associate this a record with. The DNS
        view must already be configured on the system.
    type: str
    default: default
    aliases:
      - dns_view
  order:
    description:
      - Configures the order (0-65535) for this NAPTR record. This parameter
        specifies the order in which the NAPTR rules are applied when
        multiple rules are present.
    type: int
  preference:
    description:
      - Configures the preference (0-65535) for this NAPTR record. The
        preference field determines the order NAPTR records are processed
        when multiple records with the same order parameter are present.
    type: int
  replacement:
    description:
      - Configures the replacement field for this NAPTR record.
        For nonterminal NAPTR records, this field specifies the
        next domain name to look up.
    type: str
  services:
    description:
      - Configures the services field (128 characters maximum) for this
        NAPTR record. The services field contains protocol and service
        identifiers, such as "http+E2U" or "SIPS+D2T".
    type: str
  flags:
    description:
      - Configures the flags field for this NAPTR record. These control the
        interpretation of the fields for an NAPTR record object. Supported
        values for the flags field are "U", "S", "P" and "A".
    type: str
  regexp:
    description:
      - Configures the regexp field for this NAPTR record. This is the
        regular expression-based rewriting rule of the NAPTR record. This
        should be a POSIX compliant regular expression, including the
        substitution rule and flags. Refer to RFC 2915 for the field syntax
        details.
    type: str
  ttl:
    description:
      - Configures the TTL to be associated with this NAPTR record.
    type: int
  extattrs:
    description:
      - Allows for the configuration of Extensible Attributes on the
        instance of the object.  This argument accepts a set of key / value
        pairs for configuration.
    type: dict
  comment:
    description:
      - Configures a text string comment to be associated with the instance
        of this object.  The provided text string will be configured on the
        object instance.
    type: str
  state:
    description:
      - Configures the intended state of the instance of the object on
        the NIOS server.  When this value is set to C(present), the object
        is configured on the device and when this value is set to C(absent)
        the value is removed (if necessary) from the device.
    type: str
    default: present
    choices:
      - present
      - absent
'''

EXAMPLES = '''
- name: Configure an NAPTR record
  infoblox.nios_modules.nios_naptr_record:
    name: '*.subscriber-100.ansiblezone.com'
    order: 1000
    preference: 10
    replacement: replacement1.network.ansiblezone.com
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Add a comment to an existing NAPTR record
  infoblox.nios_modules.nios_naptr_record:
    name: '*.subscriber-100.ansiblezone.com'
    order: 1000
    preference: 10
    replacement: replacement1.network.ansiblezone.com
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove an NAPTR record from the system
  infoblox.nios_modules.nios_naptr_record:
    name: '*.subscriber-100.ansiblezone.com'
    order: 1000
    preference: 10
    replacement: replacement1.network.ansiblezone.com
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from ..module_utils.api import WapiModule
from ..module_utils.api import normalize_ib_spec


def main():
    ''' Main entry point for module execution
    '''

    ib_spec = dict(
        name=dict(required=True, ib_req=True),
        view=dict(default='default', aliases=['dns_view'], ib_req=True),

        order=dict(type='int', ib_req=True),
        preference=dict(type='int', ib_req=True),
        replacement=dict(ib_req=True),
        services=dict(),
        flags=dict(),
        regexp=dict(),

        ttl=dict(type='int'),

        extattrs=dict(type='dict'),
        comment=dict(),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(normalize_ib_spec(ib_spec))
    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    wapi = WapiModule(module)
    result = wapi.run('record:naptr', ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
