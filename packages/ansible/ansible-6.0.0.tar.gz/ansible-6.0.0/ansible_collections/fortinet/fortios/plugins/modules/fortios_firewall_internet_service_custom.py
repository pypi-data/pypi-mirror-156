#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
# Copyright: (c) 2022 Fortinet
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: fortios_firewall_internet_service_custom
short_description: Configure custom Internet Services in Fortinet's FortiOS and FortiGate.
description:
    - This module is able to configure a FortiGate or FortiOS (FOS) device by allowing the
      user to set and modify firewall feature and internet_service_custom category.
      Examples include all parameters and values need to be adjusted to datasources before usage.
      Tested with FOS v6.0.0
version_added: "2.0.0"
author:
    - Link Zheng (@chillancezen)
    - Jie Xue (@JieX19)
    - Hongbin Lu (@fgtdev-hblu)
    - Frank Shen (@frankshen01)
    - Miguel Angel Munoz (@mamunozgonzalez)
    - Nicolas Thomas (@thomnico)
notes:
    - Legacy fortiosapi has been deprecated, httpapi is the preferred way to run playbooks

requirements:
    - ansible>=2.9.0
options:
    access_token:
        description:
            - Token-based authentication.
              Generated from GUI of Fortigate.
        type: str
        required: false
    enable_log:
        description:
            - Enable/Disable logging for task.
        type: bool
        required: false
        default: false
    vdom:
        description:
            - Virtual domain, among those defined previously. A vdom is a
              virtual instance of the FortiGate that can be configured and
              used as a different unit.
        type: str
        default: root
    member_path:
        type: str
        description:
            - Member attribute path to operate on.
            - Delimited by a slash character if there are more than one attribute.
            - Parameter marked with member_path is legitimate for doing member operation.
    member_state:
        type: str
        description:
            - Add or delete a member under specified attribute path.
            - When member_state is specified, the state option is ignored.
        choices:
            - present
            - absent

    state:
        description:
            - Indicates whether to create or remove the object.
        type: str
        required: true
        choices:
            - present
            - absent
    firewall_internet_service_custom:
        description:
            - Configure custom Internet Services.
        default: null
        type: dict
        suboptions:
            comment:
                description:
                    - Comment.
                type: str
            disable_entry:
                description:
                    - Disable entries in the Internet Service database.
                type: list
                elements: dict
                suboptions:
                    id:
                        description:
                            - Disable entry ID.
                        required: true
                        type: int
                    ip_range:
                        description:
                            - IP ranges in the disable entry.
                        type: list
                        elements: dict
                        suboptions:
                            end_ip:
                                description:
                                    - End IP address.
                                type: str
                            id:
                                description:
                                    - Disable entry range ID.
                                required: true
                                type: int
                            start_ip:
                                description:
                                    - Start IP address.
                                type: str
                    port:
                        description:
                            - Integer value for the TCP/IP port (0 - 65535).
                        type: int
                    protocol:
                        description:
                            - Integer value for the protocol type as defined by IANA (0 - 255).
                        type: int
            entry:
                description:
                    - Entries added to the Internet Service database and custom database.
                type: list
                elements: dict
                suboptions:
                    dst:
                        description:
                            - Destination address or address group name.
                        type: list
                        elements: dict
                        suboptions:
                            name:
                                description:
                                    - Select the destination address or address group object from available options. Source firewall.address.name firewall
                                      .addrgrp.name.
                                required: true
                                type: str
                    id:
                        description:
                            - Entry ID(1-255).
                        required: true
                        type: int
                    port_range:
                        description:
                            - Port ranges in the custom entry.
                        type: list
                        elements: dict
                        suboptions:
                            end_port:
                                description:
                                    - Integer value for ending TCP/UDP/SCTP destination port in range (1 to 65535).
                                type: int
                            id:
                                description:
                                    - Custom entry port range ID.
                                required: true
                                type: int
                            start_port:
                                description:
                                    - Integer value for starting TCP/UDP/SCTP destination port in range (1 to 65535).
                                type: int
                    protocol:
                        description:
                            - Integer value for the protocol type as defined by IANA (0 - 255).
                        type: int
            master_service_id:
                description:
                    - Internet Service ID in the Internet Service database. Source firewall.internet-service.id.
                type: int
            name:
                description:
                    - Internet Service name.
                required: true
                type: str
            reputation:
                description:
                    - Reputation level of the custom Internet Service. Source firewall.internet-service-reputation.id.
                type: int
'''

EXAMPLES = '''
- hosts: fortigates
  collections:
    - fortinet.fortios
  connection: httpapi
  vars:
   vdom: "root"
   ansible_httpapi_use_ssl: yes
   ansible_httpapi_validate_certs: no
   ansible_httpapi_port: 443
  tasks:
  - name: Configure custom Internet Services.
    fortios_firewall_internet_service_custom:
      vdom:  "{{ vdom }}"
      state: "present"
      access_token: "<your_own_value>"
      firewall_internet_service_custom:
        comment: "Comment."
        disable_entry:
         -
            id:  "5"
            ip_range:
             -
                end_ip: "<your_own_value>"
                id:  "8"
                start_ip: "<your_own_value>"
            port: "10"
            protocol: "11"
        entry:
         -
            dst:
             -
                name: "default_name_14 (source firewall.address.name firewall.addrgrp.name)"
            id:  "15"
            port_range:
             -
                end_port: "17"
                id:  "18"
                start_port: "19"
            protocol: "20"
        master_service_id: "21 (source firewall.internet-service.id)"
        name: "default_name_22"
        reputation: "23 (source firewall.internet-service-reputation.id)"

'''

RETURN = '''
build:
  description: Build number of the fortigate image
  returned: always
  type: str
  sample: '1547'
http_method:
  description: Last method used to provision the content into FortiGate
  returned: always
  type: str
  sample: 'PUT'
http_status:
  description: Last result given by FortiGate on last operation applied
  returned: always
  type: str
  sample: "200"
mkey:
  description: Master key (id) used in the last call to FortiGate
  returned: success
  type: str
  sample: "id"
name:
  description: Name of the table used to fulfill the request
  returned: always
  type: str
  sample: "urlfilter"
path:
  description: Path of the table used to fulfill the request
  returned: always
  type: str
  sample: "webfilter"
revision:
  description: Internal revision number
  returned: always
  type: str
  sample: "17.0.2.10658"
serial:
  description: Serial number of the unit
  returned: always
  type: str
  sample: "FGVMEVYYQT3AB5352"
status:
  description: Indication of the operation's result
  returned: always
  type: str
  sample: "success"
vdom:
  description: Virtual domain used
  returned: always
  type: str
  sample: "root"
version:
  description: Version of the FortiGate
  returned: always
  type: str
  sample: "v5.6.3"

'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible_collections.fortinet.fortios.plugins.module_utils.fortios.fortios import FortiOSHandler
from ansible_collections.fortinet.fortios.plugins.module_utils.fortios.fortios import check_legacy_fortiosapi
from ansible_collections.fortinet.fortios.plugins.module_utils.fortios.fortios import schema_to_module_spec
from ansible_collections.fortinet.fortios.plugins.module_utils.fortios.fortios import check_schema_versioning
from ansible_collections.fortinet.fortios.plugins.module_utils.fortimanager.common import FAIL_SOCKET_MSG
from ansible_collections.fortinet.fortios.plugins.module_utils.fortios.comparison import is_same_comparison
from ansible_collections.fortinet.fortios.plugins.module_utils.fortios.comparison import serialize


def filter_firewall_internet_service_custom_data(json):
    option_list = ['comment', 'disable_entry', 'entry',
                   'master_service_id', 'name', 'reputation']
    dictionary = {}

    for attribute in option_list:
        if attribute in json and json[attribute] is not None:
            dictionary[attribute] = json[attribute]

    return dictionary


def underscore_to_hyphen(data):
    if isinstance(data, list):
        for i, elem in enumerate(data):
            data[i] = underscore_to_hyphen(elem)
    elif isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            new_data[k.replace('_', '-')] = underscore_to_hyphen(v)
        data = new_data

    return data


def firewall_internet_service_custom(data, fos, check_mode=False):

    vdom = data['vdom']

    state = data['state']

    firewall_internet_service_custom_data = data['firewall_internet_service_custom']
    filtered_data = underscore_to_hyphen(filter_firewall_internet_service_custom_data(firewall_internet_service_custom_data))

    # check_mode starts from here
    if check_mode:
        mkey = fos.get_mkey('firewall', 'internet-service-custom', filtered_data, vdom=vdom)
        current_data = fos.get('firewall', 'internet-service-custom', vdom=vdom, mkey=mkey)
        is_existed = current_data and current_data.get('http_status') == 200 \
            and isinstance(current_data.get('results'), list) \
            and len(current_data['results']) > 0

        # 2. if it exists and the state is 'present' then compare current settings with desired
        if state == 'present' or state is True:
            if mkey is None:
                return False, True, filtered_data

            # if mkey exists then compare each other
            # record exits and they're matched or not
            if is_existed:
                is_same = is_same_comparison(
                    serialize(current_data['results'][0]), serialize(filtered_data))
                return False, not is_same, filtered_data

            # record does not exist
            return False, True, filtered_data

        if state == 'absent':
            if mkey is None:
                return False, False, filtered_data

            if is_existed:
                return False, True, filtered_data
            return False, False, filtered_data

        return True, False, {'reason: ': 'Must provide state parameter'}

    if state == "present" or state is True:
        return fos.set('firewall',
                       'internet-service-custom',
                       data=filtered_data,
                       vdom=vdom)

    elif state == "absent":
        return fos.delete('firewall',
                          'internet-service-custom',
                          mkey=filtered_data['name'],
                          vdom=vdom)
    else:
        fos._module.fail_json(msg='state must be present or absent!')


def is_successful_status(resp):
    return 'status' in resp and resp['status'] == 'success' or \
        'http_status' in resp and resp['http_status'] == 200 or \
        'http_method' in resp and resp['http_method'] == "DELETE" and resp['http_status'] == 404


def fortios_firewall(data, fos, check_mode):

    fos.do_member_operation('firewall', 'internet-service-custom')
    if data['firewall_internet_service_custom']:
        resp = firewall_internet_service_custom(data, fos, check_mode)
    else:
        fos._module.fail_json(msg='missing task body: %s' % ('firewall_internet_service_custom'))
    if check_mode:
        return resp
    return not is_successful_status(resp), \
        is_successful_status(resp) and \
        (resp['revision_changed'] if 'revision_changed' in resp else True), \
        resp


versioned_schema = {
    "elements": "dict",
    "type": "list",
    "children": {
        "comment": {
            "type": "string",
            "revisions": {
                "v7.0.3": True,
                "v7.0.2": True,
                "v7.0.1": True,
                "v7.0.0": True,
                "v7.0.5": True,
                "v7.0.4": True,
                "v6.4.4": True,
                "v6.0.5": True,
                "v6.0.0": True,
                "v6.4.0": True,
                "v6.4.1": True,
                "v6.2.0": True,
                "v6.2.3": True,
                "v6.2.5": True,
                "v6.2.7": True,
                "v6.0.11": True
            }
        },
        "name": {
            "type": "string",
            "revisions": {
                "v7.0.3": True,
                "v7.0.2": True,
                "v7.0.1": True,
                "v7.0.0": True,
                "v7.0.5": True,
                "v7.0.4": True,
                "v6.4.4": True,
                "v6.0.5": True,
                "v6.0.0": True,
                "v6.4.0": True,
                "v6.4.1": True,
                "v6.2.0": True,
                "v6.2.3": True,
                "v6.2.5": True,
                "v6.2.7": True,
                "v6.0.11": True
            }
        },
        "master_service_id": {
            "type": "integer",
            "revisions": {
                "v6.0.11": True,
                "v6.0.0": True,
                "v6.0.5": True
            }
        },
        "disable_entry": {
            "elements": "dict",
            "type": "list",
            "children": {
                "port": {
                    "type": "integer",
                    "revisions": {
                        "v6.0.11": True,
                        "v6.0.0": True,
                        "v6.0.5": True
                    }
                },
                "protocol": {
                    "type": "integer",
                    "revisions": {
                        "v6.0.11": True,
                        "v6.0.0": True,
                        "v6.0.5": True
                    }
                },
                "ip_range": {
                    "elements": "dict",
                    "type": "list",
                    "children": {
                        "start_ip": {
                            "type": "string",
                            "revisions": {
                                "v6.0.11": True,
                                "v6.0.0": True,
                                "v6.0.5": True
                            }
                        },
                        "end_ip": {
                            "type": "string",
                            "revisions": {
                                "v6.0.11": True,
                                "v6.0.0": True,
                                "v6.0.5": True
                            }
                        },
                        "id": {
                            "type": "integer",
                            "revisions": {
                                "v6.0.11": True,
                                "v6.0.0": True,
                                "v6.0.5": True
                            }
                        }
                    },
                    "revisions": {
                        "v6.0.11": True,
                        "v6.0.0": True,
                        "v6.0.5": True
                    }
                },
                "id": {
                    "type": "integer",
                    "revisions": {
                        "v6.0.11": True,
                        "v6.0.0": True,
                        "v6.0.5": True
                    }
                }
            },
            "revisions": {
                "v6.0.11": True,
                "v6.0.0": True,
                "v6.0.5": True
            }
        },
        "reputation": {
            "type": "integer",
            "revisions": {
                "v7.0.3": True,
                "v7.0.2": True,
                "v7.0.1": True,
                "v7.0.0": True,
                "v7.0.5": True,
                "v7.0.4": True,
                "v6.4.4": True,
                "v6.0.5": False,
                "v6.0.0": False,
                "v6.4.0": True,
                "v6.4.1": True,
                "v6.2.0": True,
                "v6.2.3": True,
                "v6.2.5": True,
                "v6.2.7": True,
                "v6.0.11": False
            }
        },
        "entry": {
            "elements": "dict",
            "type": "list",
            "children": {
                "port_range": {
                    "elements": "dict",
                    "type": "list",
                    "children": {
                        "end_port": {
                            "type": "integer",
                            "revisions": {
                                "v7.0.3": True,
                                "v7.0.2": True,
                                "v7.0.1": True,
                                "v7.0.0": True,
                                "v7.0.5": True,
                                "v7.0.4": True,
                                "v6.4.4": True,
                                "v6.0.5": True,
                                "v6.0.0": True,
                                "v6.4.0": True,
                                "v6.4.1": True,
                                "v6.2.0": True,
                                "v6.2.3": True,
                                "v6.2.5": True,
                                "v6.2.7": True,
                                "v6.0.11": True
                            }
                        },
                        "start_port": {
                            "type": "integer",
                            "revisions": {
                                "v7.0.3": True,
                                "v7.0.2": True,
                                "v7.0.1": True,
                                "v7.0.0": True,
                                "v7.0.5": True,
                                "v7.0.4": True,
                                "v6.4.4": True,
                                "v6.0.5": True,
                                "v6.0.0": True,
                                "v6.4.0": True,
                                "v6.4.1": True,
                                "v6.2.0": True,
                                "v6.2.3": True,
                                "v6.2.5": True,
                                "v6.2.7": True,
                                "v6.0.11": True
                            }
                        },
                        "id": {
                            "type": "integer",
                            "revisions": {
                                "v7.0.3": True,
                                "v7.0.2": True,
                                "v7.0.1": True,
                                "v7.0.0": True,
                                "v7.0.5": True,
                                "v7.0.4": True,
                                "v6.4.4": True,
                                "v6.0.5": True,
                                "v6.0.0": True,
                                "v6.4.0": True,
                                "v6.4.1": True,
                                "v6.2.0": True,
                                "v6.2.3": True,
                                "v6.2.5": True,
                                "v6.2.7": True,
                                "v6.0.11": True
                            }
                        }
                    },
                    "revisions": {
                        "v7.0.3": True,
                        "v7.0.2": True,
                        "v7.0.1": True,
                        "v7.0.0": True,
                        "v7.0.5": True,
                        "v7.0.4": True,
                        "v6.4.4": True,
                        "v6.0.5": True,
                        "v6.0.0": True,
                        "v6.4.0": True,
                        "v6.4.1": True,
                        "v6.2.0": True,
                        "v6.2.3": True,
                        "v6.2.5": True,
                        "v6.2.7": True,
                        "v6.0.11": True
                    }
                },
                "dst": {
                    "elements": "dict",
                    "type": "list",
                    "children": {
                        "name": {
                            "type": "string",
                            "revisions": {
                                "v7.0.3": True,
                                "v7.0.2": True,
                                "v7.0.1": True,
                                "v7.0.0": True,
                                "v7.0.5": True,
                                "v7.0.4": True,
                                "v6.4.4": True,
                                "v6.0.5": True,
                                "v6.0.0": True,
                                "v6.4.0": True,
                                "v6.4.1": True,
                                "v6.2.0": True,
                                "v6.2.3": True,
                                "v6.2.5": True,
                                "v6.2.7": True,
                                "v6.0.11": True
                            }
                        }
                    },
                    "revisions": {
                        "v7.0.3": True,
                        "v7.0.2": True,
                        "v7.0.1": True,
                        "v7.0.0": True,
                        "v7.0.5": True,
                        "v7.0.4": True,
                        "v6.4.4": True,
                        "v6.0.5": True,
                        "v6.0.0": True,
                        "v6.4.0": True,
                        "v6.4.1": True,
                        "v6.2.0": True,
                        "v6.2.3": True,
                        "v6.2.5": True,
                        "v6.2.7": True,
                        "v6.0.11": True
                    }
                },
                "protocol": {
                    "type": "integer",
                    "revisions": {
                        "v7.0.3": True,
                        "v7.0.2": True,
                        "v7.0.1": True,
                        "v7.0.0": True,
                        "v7.0.5": True,
                        "v7.0.4": True,
                        "v6.4.4": True,
                        "v6.0.5": True,
                        "v6.0.0": True,
                        "v6.4.0": True,
                        "v6.4.1": True,
                        "v6.2.0": True,
                        "v6.2.3": True,
                        "v6.2.5": True,
                        "v6.2.7": True,
                        "v6.0.11": True
                    }
                },
                "id": {
                    "type": "integer",
                    "revisions": {
                        "v7.0.3": True,
                        "v7.0.2": True,
                        "v7.0.1": True,
                        "v7.0.0": True,
                        "v7.0.5": True,
                        "v7.0.4": True,
                        "v6.4.4": True,
                        "v6.0.5": True,
                        "v6.0.0": True,
                        "v6.4.0": True,
                        "v6.4.1": True,
                        "v6.2.0": True,
                        "v6.2.3": True,
                        "v6.2.5": True,
                        "v6.2.7": True,
                        "v6.0.11": True
                    }
                }
            },
            "revisions": {
                "v7.0.3": True,
                "v7.0.2": True,
                "v7.0.1": True,
                "v7.0.0": True,
                "v7.0.5": True,
                "v7.0.4": True,
                "v6.4.4": True,
                "v6.0.5": True,
                "v6.0.0": True,
                "v6.4.0": True,
                "v6.4.1": True,
                "v6.2.0": True,
                "v6.2.3": True,
                "v6.2.5": True,
                "v6.2.7": True,
                "v6.0.11": True
            }
        }
    },
    "revisions": {
        "v7.0.3": True,
        "v7.0.2": True,
        "v7.0.1": True,
        "v7.0.0": True,
        "v7.0.5": True,
        "v7.0.4": True,
        "v6.4.4": True,
        "v6.0.5": True,
        "v6.0.0": True,
        "v6.4.0": True,
        "v6.4.1": True,
        "v6.2.0": True,
        "v6.2.3": True,
        "v6.2.5": True,
        "v6.2.7": True,
        "v6.0.11": True
    }
}


def main():
    module_spec = schema_to_module_spec(versioned_schema)
    mkeyname = 'name'
    fields = {
        "access_token": {"required": False, "type": "str", "no_log": True},
        "enable_log": {"required": False, "type": 'bool', "default": False},
        "vdom": {"required": False, "type": "str", "default": "root"},
        "member_path": {"required": False, "type": "str"},
        "member_state": {
            "type": "str",
            "required": False,
            "choices": ["present", "absent"]
        },
        "state": {"required": True, "type": "str",
                  "choices": ["present", "absent"]},
        "firewall_internet_service_custom": {
            "required": False, "type": "dict", "default": None,
            "options": {
            }
        }
    }
    for attribute_name in module_spec['options']:
        fields["firewall_internet_service_custom"]['options'][attribute_name] = module_spec['options'][attribute_name]
        if mkeyname and mkeyname == attribute_name:
            fields["firewall_internet_service_custom"]['options'][attribute_name]['required'] = True

    module = AnsibleModule(argument_spec=fields,
                           supports_check_mode=True)
    check_legacy_fortiosapi(module)

    versions_check_result = None
    if module._socket_path:
        connection = Connection(module._socket_path)
        if 'access_token' in module.params:
            connection.set_option('access_token', module.params['access_token'])

        if 'enable_log' in module.params:
            connection.set_option('enable_log', module.params['enable_log'])
        else:
            connection.set_option('enable_log', False)
        fos = FortiOSHandler(connection, module, mkeyname)
        versions_check_result = check_schema_versioning(fos, versioned_schema, "firewall_internet_service_custom")

        is_error, has_changed, result = fortios_firewall(module.params, fos, module.check_mode)

    else:
        module.fail_json(**FAIL_SOCKET_MSG)

    if versions_check_result and versions_check_result['matched'] is False:
        module.warn("Ansible has detected version mismatch between FortOS system and your playbook, see more details by specifying option -vvv")

    if not is_error:
        if versions_check_result and versions_check_result['matched'] is False:
            module.exit_json(changed=has_changed, version_check_warning=versions_check_result, meta=result)
        else:
            module.exit_json(changed=has_changed, meta=result)
    else:
        if versions_check_result and versions_check_result['matched'] is False:
            module.fail_json(msg="Error in repo", version_check_warning=versions_check_result, meta=result)
        else:
            module.fail_json(msg="Error in repo", meta=result)


if __name__ == '__main__':
    main()
