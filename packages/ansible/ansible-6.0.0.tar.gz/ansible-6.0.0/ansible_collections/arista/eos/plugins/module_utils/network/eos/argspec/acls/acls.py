#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#############################################
"""
The arg spec for the eos_acls module
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class AclsArgs(object):  # pylint: disable=R0903
    """The arg spec for the eos_acls module"""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "elements": "dict",
            "options": {
                "acls": {
                    "elements": "dict",
                    "options": {
                        "aces": {
                            "elements": "dict",
                            "options": {
                                "destination": {
                                    "mutually_exclusive": [
                                        [
                                            "address",
                                            "subnet_address",
                                            "any",
                                            "host",
                                        ],
                                        [
                                            "wildcard_bits",
                                            "subnet_address",
                                            "any",
                                            "host",
                                        ],
                                    ],
                                    "options": {
                                        "address": {"type": "str"},
                                        "any": {"type": "bool"},
                                        "host": {"type": "str"},
                                        "port_protocol": {"type": "dict"},
                                        "subnet_address": {"type": "str"},
                                        "wildcard_bits": {"type": "str"},
                                    },
                                    "required_together": [
                                        ["address", "wildcard_bits"]
                                    ],
                                    "type": "dict",
                                },
                                "fragment_rules": {"type": "bool"},
                                "fragments": {"type": "bool"},
                                "grant": {
                                    "choices": ["permit", "deny"],
                                    "type": "str",
                                },
                                "line": {"type": "str", "aliases": ["ace"]},
                                "hop_limit": {"type": "dict"},
                                "log": {"type": "bool"},
                                "protocol": {"type": "str"},
                                "protocol_options": {
                                    "options": {
                                        "icmp": {
                                            "options": {
                                                "administratively_prohibited": {
                                                    "type": "bool"
                                                },
                                                "alternate_address": {
                                                    "type": "bool"
                                                },
                                                "conversion_error": {
                                                    "type": "bool"
                                                },
                                                "dod_host_prohibited": {
                                                    "type": "bool"
                                                },
                                                "dod_net_prohibited": {
                                                    "type": "bool"
                                                },
                                                "echo": {"type": "bool"},
                                                "echo_reply": {"type": "bool"},
                                                "general_parameter_problem": {
                                                    "type": "bool"
                                                },
                                                "host_isolated": {
                                                    "type": "bool"
                                                },
                                                "host_precedence_unreachable": {
                                                    "type": "bool"
                                                },
                                                "host_redirect": {
                                                    "type": "bool"
                                                },
                                                "host_tos_redirect": {
                                                    "type": "bool"
                                                },
                                                "host_tos_unreachable": {
                                                    "type": "bool"
                                                },
                                                "host_unknown": {
                                                    "type": "bool"
                                                },
                                                "host_unreachable": {
                                                    "type": "bool"
                                                },
                                                "information_reply": {
                                                    "type": "bool"
                                                },
                                                "information_request": {
                                                    "type": "bool"
                                                },
                                                "mask_reply": {"type": "bool"},
                                                "mask_request": {
                                                    "type": "bool"
                                                },
                                                "message_code": {
                                                    "type": "int"
                                                },
                                                "message_num": {"type": "int"},
                                                "message_type": {
                                                    "type": "int"
                                                },
                                                "mobile_redirect": {
                                                    "type": "bool"
                                                },
                                                "net_redirect": {
                                                    "type": "bool"
                                                },
                                                "net_tos_redirect": {
                                                    "type": "bool"
                                                },
                                                "net_tos_unreachable": {
                                                    "type": "bool"
                                                },
                                                "net_unreachable": {
                                                    "type": "bool"
                                                },
                                                "network_unknown": {
                                                    "type": "bool"
                                                },
                                                "no_room_for_option": {
                                                    "type": "bool"
                                                },
                                                "option_missing": {
                                                    "type": "bool"
                                                },
                                                "packet_too_big": {
                                                    "type": "bool"
                                                },
                                                "parameter_problem": {
                                                    "type": "bool"
                                                },
                                                "port_unreachable": {
                                                    "type": "bool"
                                                },
                                                "precedence_unreachable": {
                                                    "type": "bool"
                                                },
                                                "protocol_unreachable": {
                                                    "type": "bool"
                                                },
                                                "reassembly_timeout": {
                                                    "type": "bool"
                                                },
                                                "redirect": {"type": "bool"},
                                                "router_advertisement": {
                                                    "type": "bool"
                                                },
                                                "router_solicitation": {
                                                    "type": "bool"
                                                },
                                                "source_quench": {
                                                    "type": "bool"
                                                },
                                                "source_route_failed": {
                                                    "type": "bool"
                                                },
                                                "time_exceeded": {
                                                    "type": "bool"
                                                },
                                                "timestamp_reply": {
                                                    "type": "bool"
                                                },
                                                "timestamp_request": {
                                                    "type": "bool"
                                                },
                                                "traceroute": {"type": "bool"},
                                                "ttl_exceeded": {
                                                    "type": "bool"
                                                },
                                                "unreachable": {
                                                    "type": "bool"
                                                },
                                            },
                                            "type": "dict",
                                        },
                                        "icmpv6": {
                                            "options": {
                                                "address_unreachable": {
                                                    "type": "bool"
                                                },
                                                "beyond_scope": {
                                                    "type": "bool"
                                                },
                                                "echo_reply": {"type": "bool"},
                                                "echo_request": {
                                                    "type": "bool"
                                                },
                                                "erroneous_header": {
                                                    "type": "bool"
                                                },
                                                "fragment_reassembly_exceeded": {
                                                    "type": "bool"
                                                },
                                                "hop_limit_exceeded": {
                                                    "type": "bool"
                                                },
                                                "neighbor_advertisement": {
                                                    "type": "bool"
                                                },
                                                "neighbor_solicitation": {
                                                    "type": "bool"
                                                },
                                                "no_admin": {"type": "bool"},
                                                "no_route": {"type": "bool"},
                                                "packet_too_big": {
                                                    "type": "bool"
                                                },
                                                "parameter_problem": {
                                                    "type": "bool"
                                                },
                                                "port_unreachable": {
                                                    "type": "bool"
                                                },
                                                "redirect_message": {
                                                    "type": "bool"
                                                },
                                                "reject_route": {
                                                    "type": "bool"
                                                },
                                                "router_advertisement": {
                                                    "type": "bool"
                                                },
                                                "router_solicitation": {
                                                    "type": "bool"
                                                },
                                                "source_address_failed": {
                                                    "type": "bool"
                                                },
                                                "source_routing_error": {
                                                    "type": "bool"
                                                },
                                                "time_exceeded": {
                                                    "type": "bool"
                                                },
                                                "unreachable": {
                                                    "type": "bool"
                                                },
                                                "unrecognized_ipv6_option": {
                                                    "type": "bool"
                                                },
                                                "unrecognized_next_header": {
                                                    "type": "bool"
                                                },
                                            },
                                            "type": "dict",
                                        },
                                        "ip": {
                                            "options": {
                                                "nexthop_group": {
                                                    "type": "str"
                                                }
                                            },
                                            "type": "dict",
                                        },
                                        "ipv6": {
                                            "options": {
                                                "nexthop_group": {
                                                    "type": "str"
                                                }
                                            },
                                            "type": "dict",
                                        },
                                        "tcp": {
                                            "options": {
                                                "flags": {
                                                    "options": {
                                                        "ack": {
                                                            "type": "bool"
                                                        },
                                                        "established": {
                                                            "type": "bool"
                                                        },
                                                        "fin": {
                                                            "type": "bool"
                                                        },
                                                        "psh": {
                                                            "type": "bool"
                                                        },
                                                        "rst": {
                                                            "type": "bool"
                                                        },
                                                        "syn": {
                                                            "type": "bool"
                                                        },
                                                        "urg": {
                                                            "type": "bool"
                                                        },
                                                    },
                                                    "type": "dict",
                                                }
                                            },
                                            "type": "dict",
                                        },
                                    },
                                    "type": "dict",
                                },
                                "remark": {"type": "str"},
                                "sequence": {"type": "int"},
                                "source": {
                                    "mutually_exclusive": [
                                        [
                                            "address",
                                            "subnet_address",
                                            "any",
                                            "host",
                                        ],
                                        [
                                            "wildcard_bits",
                                            "subnet_address",
                                            "any",
                                            "host",
                                        ],
                                    ],
                                    "options": {
                                        "address": {"type": "str"},
                                        "any": {"type": "bool"},
                                        "host": {"type": "str"},
                                        "port_protocol": {"type": "dict"},
                                        "subnet_address": {"type": "str"},
                                        "wildcard_bits": {"type": "str"},
                                    },
                                    "required_together": [
                                        ["address", "wildcard_bits"]
                                    ],
                                    "type": "dict",
                                },
                                "tracked": {"type": "bool"},
                                "ttl": {
                                    "options": {
                                        "eq": {"type": "int"},
                                        "gt": {"type": "int"},
                                        "lt": {"type": "int"},
                                        "neq": {"type": "int"},
                                    },
                                    "type": "dict",
                                },
                                "vlan": {"type": "str"},
                            },
                            "type": "list",
                        },
                        "name": {"required": True, "type": "str"},
                        "standard": {"type": "bool"},
                    },
                    "type": "list",
                },
                "afi": {
                    "choices": ["ipv4", "ipv6"],
                    "required": True,
                    "type": "str",
                },
            },
            "type": "list",
        },
        "running_config": {"type": "str"},
        "state": {
            "choices": [
                "deleted",
                "merged",
                "overridden",
                "replaced",
                "gathered",
                "rendered",
                "parsed",
            ],
            "default": "merged",
            "type": "str",
        },
    }  # pylint: disable=C0301
