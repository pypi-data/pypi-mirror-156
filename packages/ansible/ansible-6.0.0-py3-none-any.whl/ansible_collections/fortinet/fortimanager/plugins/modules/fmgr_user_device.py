#!/usr/bin/python
from __future__ import absolute_import, division, print_function
# Copyright 2019-2021 Fortinet, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: fmgr_user_device
short_description: Configure devices.
description:
    - This module is able to configure a FortiManager device.
    - Examples include all parameters and values which need to be adjusted to data sources before usage.

version_added: "2.10"
author:
    - Link Zheng (@chillancezen)
    - Jie Xue (@JieX19)
    - Frank Shen (@fshen01)
    - Hongbin Lu (@fgtdev-hblu)
notes:
    - Running in workspace locking mode is supported in this FortiManager module, the top
      level parameters workspace_locking_adom and workspace_locking_timeout help do the work.
    - To create or update an object, use state present directive.
    - To delete an object, use state absent directive.
    - Normally, running one module can fail when a non-zero rc is returned. you can also override
      the conditions to fail or succeed with parameters rc_failed and rc_succeeded

options:
    enable_log:
        description: Enable/Disable logging for task
        required: false
        type: bool
        default: false
    proposed_method:
        description: The overridden method for the underlying Json RPC request
        required: false
        type: str
        choices:
          - update
          - set
          - add
    bypass_validation:
        description: only set to True when module schema diffs with FortiManager API structure, module continues to execute without validating parameters
        required: false
        type: bool
        default: false
    workspace_locking_adom:
        description: the adom to lock for FortiManager running in workspace mode, the value can be global and others including root
        required: false
        type: str
    workspace_locking_timeout:
        description: the maximum time in seconds to wait for other user to release the workspace lock
        required: false
        type: int
        default: 300
    state:
        description: the directive to create, update or delete an object
        type: str
        required: true
        choices:
          - present
          - absent
    rc_succeeded:
        description: the rc codes list with which the conditions to succeed will be overriden
        type: list
        required: false
    rc_failed:
        description: the rc codes list with which the conditions to fail will be overriden
        type: list
        required: false
    adom:
        description: the parameter (adom) in requested url
        type: str
        required: true
    user_device:
        description: the top level parameters set
        required: false
        type: dict
        suboptions:
            alias:
                type: str
                description: 'Device alias.'
            avatar:
                type: str
                description: 'Image file for avatar (maximum 4K base64 encoded).'
            category:
                type: str
                description: 'Device category.'
                choices:
                    - 'none'
                    - 'android-device'
                    - 'blackberry-device'
                    - 'fortinet-device'
                    - 'ios-device'
                    - 'windows-device'
                    - 'amazon-device'
            comment:
                type: str
                description: 'Comment.'
            dynamic_mapping:
                description: 'Dynamic_Mapping.'
                type: list
                suboptions:
                    _scope:
                        description: '_Scope.'
                        type: list
                        suboptions:
                            name:
                                type: str
                                description: 'Name.'
                            vdom:
                                type: str
                                description: 'Vdom.'
                    avatar:
                        type: str
                        description: 'Image file for avatar (maximum 4K base64 encoded).'
                    category:
                        type: str
                        description: 'Family.'
                        choices:
                            - 'none'
                            - 'android-device'
                            - 'blackberry-device'
                            - 'fortinet-device'
                            - 'ios-device'
                            - 'windows-device'
                            - 'amazon-device'
                    comment:
                        type: str
                        description: 'Comment.'
                    mac:
                        type: str
                        description: 'Device MAC address.'
                    master-device:
                        type: str
                        description: 'Master device (optional).'
                    tags:
                        type: str
                        description: 'Tags.'
                    type:
                        type: str
                        description: 'Type.'
                        choices:
                            - 'ipad'
                            - 'iphone'
                            - 'gaming-console'
                            - 'blackberry-phone'
                            - 'blackberry-playbook'
                            - 'linux-pc'
                            - 'mac'
                            - 'windows-pc'
                            - 'android-phone'
                            - 'android-tablet'
                            - 'media-streaming'
                            - 'windows-phone'
                            - 'fortinet-device'
                            - 'ip-phone'
                            - 'router-nat-device'
                            - 'other-network-device'
                            - 'windows-tablet'
                            - 'printer'
                            - 'forticam'
                            - 'fortifone'
                            - 'unknown'
                    user:
                        type: str
                        description: 'User name.'
                    family:
                        type: str
                        description: 'Family.'
                    hardware-vendor:
                        type: str
                        description: 'Hardware-Vendor.'
                    hardware-version:
                        type: str
                        description: 'Hardware-Version.'
                    os:
                        type: str
                        description: 'Os.'
                    software-version:
                        type: str
                        description: 'Software-Version.'
            mac:
                type: str
                description: 'Device MAC address(es).'
            master-device:
                type: str
                description: 'Master device (optional).'
            tagging:
                description: 'Tagging.'
                type: list
                suboptions:
                    category:
                        type: str
                        description: 'Tag category.'
                    name:
                        type: str
                        description: 'Tagging entry name.'
                    tags:
                        description: 'Tags.'
                        type: str
            type:
                type: str
                description: 'Device type.'
                choices:
                    - 'ipad'
                    - 'iphone'
                    - 'gaming-console'
                    - 'blackberry-phone'
                    - 'blackberry-playbook'
                    - 'linux-pc'
                    - 'mac'
                    - 'windows-pc'
                    - 'android-phone'
                    - 'android-tablet'
                    - 'media-streaming'
                    - 'windows-phone'
                    - 'fortinet-device'
                    - 'ip-phone'
                    - 'router-nat-device'
                    - 'other-network-device'
                    - 'windows-tablet'
                    - 'printer'
                    - 'forticam'
                    - 'fortifone'
                    - 'unknown'
            user:
                type: str
                description: 'User name.'

'''

EXAMPLES = '''
 - hosts: fortimanager00
   collections:
     - fortinet.fortimanager
   connection: httpapi
   vars:
      ansible_httpapi_use_ssl: True
      ansible_httpapi_validate_certs: False
      ansible_httpapi_port: 443
   tasks:
    - name: Configure devices.
      fmgr_user_device:
         bypass_validation: False
         adom: ansible
         state: present
         user_device:
            alias: ansible-test-device
            category: android-device #<value in [none, android-device, blackberry-device, ...]>
            comment: ansible-comment
            mac: '00:11:22:33:44:55'
            type: iphone #<value in [ipad, iphone, gaming-console, ...]>

 - name: gathering fortimanager facts
   hosts: fortimanager00
   gather_facts: no
   connection: httpapi
   collections:
     - fortinet.fortimanager
   vars:
     ansible_httpapi_use_ssl: True
     ansible_httpapi_validate_certs: False
     ansible_httpapi_port: 443
   tasks:
    - name: retrieve all the devices
      fmgr_fact:
        facts:
            selector: 'user_device'
            params:
                adom: 'ansible'
                device: '' 

'''

RETURN = '''
request_url:
    description: The full url requested
    returned: always
    type: str
    sample: /sys/login/user
response_code:
    description: The status of api request
    returned: always
    type: int
    sample: 0
response_message:
    description: The descriptive message of the api response
    type: str
    returned: always
    sample: OK.

'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible_collections.fortinet.fortimanager.plugins.module_utils.napi import NAPIManager
from ansible_collections.fortinet.fortimanager.plugins.module_utils.napi import check_galaxy_version
from ansible_collections.fortinet.fortimanager.plugins.module_utils.napi import check_parameter_bypass


def main():
    jrpc_urls = [
        '/pm/config/adom/{adom}/obj/user/device',
        '/pm/config/global/obj/user/device'
    ]

    perobject_jrpc_urls = [
        '/pm/config/adom/{adom}/obj/user/device/{device}',
        '/pm/config/global/obj/user/device/{device}'
    ]

    url_params = ['adom']
    module_primary_key = 'alias'
    module_arg_spec = {
        'enable_log': {
            'type': 'bool',
            'required': False,
            'default': False
        },
        'forticloud_access_token': {
            'type': 'str',
            'required': False,
            'no_log': True
        },
        'proposed_method': {
            'type': 'str',
            'required': False,
            'choices': [
                'set',
                'update',
                'add'
            ]
        },
        'bypass_validation': {
            'type': 'bool',
            'required': False,
            'default': False
        },
        'workspace_locking_adom': {
            'type': 'str',
            'required': False
        },
        'workspace_locking_timeout': {
            'type': 'int',
            'required': False,
            'default': 300
        },
        'rc_succeeded': {
            'required': False,
            'type': 'list'
        },
        'rc_failed': {
            'required': False,
            'type': 'list'
        },
        'state': {
            'type': 'str',
            'required': True,
            'choices': [
                'present',
                'absent'
            ]
        },
        'adom': {
            'required': True,
            'type': 'str'
        },
        'user_device': {
            'required': False,
            'type': 'dict',
            'revision': {
                '6.0.0': True,
                '6.2.1': True,
                '6.2.3': True,
                '6.2.5': True
            },
            'options': {
                'alias': {
                    'required': True,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'type': 'str'
                },
                'avatar': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'type': 'str'
                },
                'category': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'choices': [
                        'none',
                        'android-device',
                        'blackberry-device',
                        'fortinet-device',
                        'ios-device',
                        'windows-device',
                        'amazon-device'
                    ],
                    'type': 'str'
                },
                'comment': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'type': 'str'
                },
                'dynamic_mapping': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'type': 'list',
                    'options': {
                        '_scope': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'list',
                            'options': {
                                'name': {
                                    'required': False,
                                    'revision': {
                                        '6.0.0': True,
                                        '6.2.1': True,
                                        '6.2.3': True,
                                        '6.2.5': True,
                                        '6.4.0': False,
                                        '6.4.2': False,
                                        '6.4.5': False,
                                        '7.0.0': False
                                    },
                                    'type': 'str'
                                },
                                'vdom': {
                                    'required': False,
                                    'revision': {
                                        '6.0.0': True,
                                        '6.2.1': True,
                                        '6.2.3': True,
                                        '6.2.5': True,
                                        '6.4.0': False,
                                        '6.4.2': False,
                                        '6.4.5': False,
                                        '7.0.0': False
                                    },
                                    'type': 'str'
                                }
                            }
                        },
                        'avatar': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'category': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'choices': [
                                'none',
                                'android-device',
                                'blackberry-device',
                                'fortinet-device',
                                'ios-device',
                                'windows-device',
                                'amazon-device'
                            ],
                            'type': 'str'
                        },
                        'comment': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'mac': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'master-device': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'tags': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'type': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'choices': [
                                'ipad',
                                'iphone',
                                'gaming-console',
                                'blackberry-phone',
                                'blackberry-playbook',
                                'linux-pc',
                                'mac',
                                'windows-pc',
                                'android-phone',
                                'android-tablet',
                                'media-streaming',
                                'windows-phone',
                                'fortinet-device',
                                'ip-phone',
                                'router-nat-device',
                                'other-network-device',
                                'windows-tablet',
                                'printer',
                                'forticam',
                                'fortifone',
                                'unknown'
                            ],
                            'type': 'str'
                        },
                        'user': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'family': {
                            'required': False,
                            'revision': {
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'hardware-vendor': {
                            'required': False,
                            'revision': {
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'hardware-version': {
                            'required': False,
                            'revision': {
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'os': {
                            'required': False,
                            'revision': {
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'software-version': {
                            'required': False,
                            'revision': {
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        }
                    }
                },
                'mac': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'type': 'str'
                },
                'master-device': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'type': 'str'
                },
                'tagging': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'type': 'list',
                    'options': {
                        'category': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'name': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        },
                        'tags': {
                            'required': False,
                            'revision': {
                                '6.0.0': True,
                                '6.2.1': True,
                                '6.2.3': True,
                                '6.2.5': True,
                                '6.4.0': False,
                                '6.4.2': False,
                                '6.4.5': False,
                                '7.0.0': False
                            },
                            'type': 'str'
                        }
                    }
                },
                'type': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'choices': [
                        'ipad',
                        'iphone',
                        'gaming-console',
                        'blackberry-phone',
                        'blackberry-playbook',
                        'linux-pc',
                        'mac',
                        'windows-pc',
                        'android-phone',
                        'android-tablet',
                        'media-streaming',
                        'windows-phone',
                        'fortinet-device',
                        'ip-phone',
                        'router-nat-device',
                        'other-network-device',
                        'windows-tablet',
                        'printer',
                        'forticam',
                        'fortifone',
                        'unknown'
                    ],
                    'type': 'str'
                },
                'user': {
                    'required': False,
                    'revision': {
                        '6.0.0': True,
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': False,
                        '6.4.2': False,
                        '6.4.5': False,
                        '7.0.0': False
                    },
                    'type': 'str'
                }
            }

        }
    }

    params_validation_blob = []
    check_galaxy_version(module_arg_spec)
    module = AnsibleModule(argument_spec=check_parameter_bypass(module_arg_spec, 'user_device'),
                           supports_check_mode=False)

    fmgr = None
    if module._socket_path:
        connection = Connection(module._socket_path)
        connection.set_option('enable_log', module.params['enable_log'] if 'enable_log' in module.params else False)
        connection.set_option('forticloud_access_token',
                              module.params['forticloud_access_token'] if 'forticloud_access_token' in module.params else None)
        fmgr = NAPIManager(jrpc_urls, perobject_jrpc_urls, module_primary_key, url_params, module, connection, top_level_schema_name='data')
        fmgr.validate_parameters(params_validation_blob)
        fmgr.process_curd(argument_specs=module_arg_spec)
    else:
        module.fail_json(msg='MUST RUN IN HTTPAPI MODE')
    module.exit_json(meta=module.params)


if __name__ == '__main__':
    main()
