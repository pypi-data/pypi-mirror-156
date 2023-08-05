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
module: fmgr_firewall_profileprotocoloptions_cifs
short_description: Configure CIFS protocol options.
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
    profile-protocol-options:
        description: the parameter (profile-protocol-options) in requested url
        type: str
        required: true
    firewall_profileprotocoloptions_cifs:
        description: the top level parameters set
        required: false
        type: dict
        suboptions:
            ports:
                description: no description
                type: int
            status:
                type: str
                description: 'Enable/disable the active status of scanning for this protocol.'
                choices:
                    - 'disable'
                    - 'enable'
            options:
                description: no description
                type: list
                choices:
                 - oversize
            oversize-limit:
                type: int
                description: 'Maximum in-memory file size that can be scanned (1 - 383 MB, default = 10).'
            scan-bzip2:
                type: str
                description: 'Enable/disable scanning of BZip2 compressed files.'
                choices:
                    - 'disable'
                    - 'enable'
            tcp-window-maximum:
                type: int
                description: 'Maximum dynamic TCP window size (default = 8MB).'
            tcp-window-minimum:
                type: int
                description: 'Minimum dynamic TCP window size (default = 128KB).'
            tcp-window-size:
                type: int
                description: 'Set TCP static window size (default = 256KB).'
            tcp-window-type:
                type: str
                description: 'Specify type of TCP window to use for this protocol.'
                choices:
                    - 'system'
                    - 'static'
                    - 'dynamic'
            uncompressed-nest-limit:
                type: int
                description: 'Maximum nested levels of compression that can be uncompressed and scanned (2 - 100, default = 12).'
            uncompressed-oversize-limit:
                type: int
                description: 'Maximum in-memory uncompressed file size that can be scanned (0 - 383 MB, 0 = unlimited, default = 10).'
            domain-controller:
                type: str
                description: 'Domain for which to decrypt CIFS traffic.'
            file-filter:
                description: no description
                type: dict
                required: false
                suboptions:
                    entries:
                        description: no description
                        type: list
                        suboptions:
                            action:
                                type: str
                                description: 'Action taken for matched file.'
                                choices:
                                    - 'log'
                                    - 'block'
                            comment:
                                type: str
                                description: 'Comment.'
                            direction:
                                type: str
                                description: 'Match files transmitted in the sessions originating or reply direction.'
                                choices:
                                    - 'any'
                                    - 'incoming'
                                    - 'outgoing'
                            file-type:
                                description: no description
                                type: str
                            filter:
                                type: str
                                description: 'Add a file filter.'
                            protocol:
                                description: no description
                                type: list
                                choices:
                                 - cifs
                    log:
                        type: str
                        description: 'Enable/disable file filter logging.'
                        choices:
                            - 'disable'
                            - 'enable'
                    status:
                        type: str
                        description: 'Enable/disable file filter.'
                        choices:
                            - 'disable'
                            - 'enable'
            server-credential-type:
                type: str
                description: 'CIFS server credential type.'
                choices:
                    - 'none'
                    - 'credential-replication'
                    - 'credential-keytab'
            server-keytab:
                description: no description
                type: list
                suboptions:
                    keytab:
                        type: str
                        description: 'Base64 encoded keytab file containing credential of the server.'
                    password:
                        description: no description
                        type: str
                    principal:
                        type: str
                        description: 'Service principal.  For example, "host/cifsserver.example.com@example.com".'

'''

EXAMPLES = '''
 - hosts: fortimanager-inventory
   collections:
     - fortinet.fortimanager
   connection: httpapi
   vars:
      ansible_httpapi_use_ssl: True
      ansible_httpapi_validate_certs: False
      ansible_httpapi_port: 443
   tasks:
    - name: Configure CIFS protocol options.
      fmgr_firewall_profileprotocoloptions_cifs:
         bypass_validation: False
         workspace_locking_adom: <value in [global, custom adom including root]>
         workspace_locking_timeout: 300
         rc_succeeded: [0, -2, -3, ...]
         rc_failed: [-2, -3, ...]
         adom: <your own value>
         profile-protocol-options: <your own value>
         firewall_profileprotocoloptions_cifs:
            ports: <value of integer>
            status: <value in [disable, enable]>
            options:
              - oversize
            oversize-limit: <value of integer>
            scan-bzip2: <value in [disable, enable]>
            tcp-window-maximum: <value of integer>
            tcp-window-minimum: <value of integer>
            tcp-window-size: <value of integer>
            tcp-window-type: <value in [system, static, dynamic]>
            uncompressed-nest-limit: <value of integer>
            uncompressed-oversize-limit: <value of integer>
            domain-controller: <value of string>
            file-filter:
               entries:
                 -
                     action: <value in [log, block]>
                     comment: <value of string>
                     direction: <value in [any, incoming, outgoing]>
                     file-type: <value of string>
                     filter: <value of string>
                     protocol:
                       - cifs
               log: <value in [disable, enable]>
               status: <value in [disable, enable]>
            server-credential-type: <value in [none, credential-replication, credential-keytab]>
            server-keytab:
              -
                  keytab: <value of string>
                  password: <value of string>
                  principal: <value of string>

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
        '/pm/config/global/obj/firewall/profile-protocol-options/{profile-protocol-options}/cifs',
        '/pm/config/adom/{adom}/obj/firewall/profile-protocol-options/{profile-protocol-options}/cifs'
    ]

    perobject_jrpc_urls = [
        '/pm/config/global/obj/firewall/profile-protocol-options/{profile-protocol-options}/cifs/{cifs}',
        '/pm/config/adom/{adom}/obj/firewall/profile-protocol-options/{profile-protocol-options}/cifs/{cifs}'
    ]

    url_params = ['adom', 'profile-protocol-options']
    module_primary_key = None
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
        'adom': {
            'required': True,
            'type': 'str'
        },
        'profile-protocol-options': {
            'required': True,
            'type': 'str'
        },
        'firewall_profileprotocoloptions_cifs': {
            'required': False,
            'type': 'dict',
            'revision': {
                '6.2.1': True,
                '6.2.3': True,
                '6.2.5': True,
                '6.4.0': True,
                '6.4.2': True,
                '6.4.5': True,
                '7.0.0': True
            },
            'options': {
                'ports': {
                    'required': False,
                    'revision': {
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'status': {
                    'required': False,
                    'revision': {
                        '6.2.1': True,
                        '6.2.3': True,
                        '6.2.5': True,
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                },
                'options': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'choices': [
                        'oversize'
                    ]
                },
                'oversize-limit': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'scan-bzip2': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'disable',
                        'enable'
                    ],
                    'type': 'str'
                },
                'tcp-window-maximum': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'tcp-window-minimum': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'tcp-window-size': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'tcp-window-type': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'system',
                        'static',
                        'dynamic'
                    ],
                    'type': 'str'
                },
                'uncompressed-nest-limit': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'uncompressed-oversize-limit': {
                    'required': False,
                    'revision': {
                        '6.4.0': True,
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'int'
                },
                'domain-controller': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'str'
                },
                'file-filter': {
                    'required': False,
                    'type': 'dict',
                    'options': {
                        'entries': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': False
                            },
                            'type': 'list',
                            'options': {
                                'action': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': False
                                    },
                                    'choices': [
                                        'log',
                                        'block'
                                    ],
                                    'type': 'str'
                                },
                                'comment': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': False
                                    },
                                    'type': 'str'
                                },
                                'direction': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': False
                                    },
                                    'choices': [
                                        'any',
                                        'incoming',
                                        'outgoing'
                                    ],
                                    'type': 'str'
                                },
                                'file-type': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': False
                                    },
                                    'type': 'str'
                                },
                                'filter': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': False
                                    },
                                    'type': 'str'
                                },
                                'protocol': {
                                    'required': False,
                                    'revision': {
                                        '6.4.2': True,
                                        '6.4.5': True,
                                        '7.0.0': False
                                    },
                                    'type': 'list',
                                    'choices': [
                                        'cifs'
                                    ]
                                }
                            }
                        },
                        'log': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': False
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        },
                        'status': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': False
                            },
                            'choices': [
                                'disable',
                                'enable'
                            ],
                            'type': 'str'
                        }
                    }
                },
                'server-credential-type': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'choices': [
                        'none',
                        'credential-replication',
                        'credential-keytab'
                    ],
                    'type': 'str'
                },
                'server-keytab': {
                    'required': False,
                    'revision': {
                        '6.4.2': True,
                        '6.4.5': True,
                        '7.0.0': True
                    },
                    'type': 'list',
                    'options': {
                        'keytab': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'password': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        },
                        'principal': {
                            'required': False,
                            'revision': {
                                '6.4.2': True,
                                '6.4.5': True,
                                '7.0.0': True
                            },
                            'type': 'str'
                        }
                    }
                }
            }

        }
    }

    params_validation_blob = []
    check_galaxy_version(module_arg_spec)
    module = AnsibleModule(argument_spec=check_parameter_bypass(module_arg_spec, 'firewall_profileprotocoloptions_cifs'),
                           supports_check_mode=False)

    fmgr = None
    if module._socket_path:
        connection = Connection(module._socket_path)
        connection.set_option('enable_log', module.params['enable_log'] if 'enable_log' in module.params else False)
        connection.set_option('forticloud_access_token',
                              module.params['forticloud_access_token'] if 'forticloud_access_token' in module.params else None)
        fmgr = NAPIManager(jrpc_urls, perobject_jrpc_urls, module_primary_key, url_params, module, connection, top_level_schema_name='data')
        fmgr.validate_parameters(params_validation_blob)
        fmgr.process_partial_curd(argument_specs=module_arg_spec)
    else:
        module.fail_json(msg='MUST RUN IN HTTPAPI MODE')
    module.exit_json(meta=module.params)


if __name__ == '__main__':
    main()
