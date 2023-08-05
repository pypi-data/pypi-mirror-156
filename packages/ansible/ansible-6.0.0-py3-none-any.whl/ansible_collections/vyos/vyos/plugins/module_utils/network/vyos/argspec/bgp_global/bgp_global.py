# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
The arg spec for the vyos_bgp_global module
"""


class Bgp_globalArgs(object):  # pylint: disable=R0903
    """The arg spec for the vyos_bgp_global module"""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "running_config": {"type": "str"},
        "state": {
            "default": "merged",
            "type": "str",
            "choices": [
                "merged",
                "replaced",
                "deleted",
                "gathered",
                "parsed",
                "rendered",
                "purged",
            ],
        },
        "config": {
            "type": "dict",
            "options": {
                "redistribute": {
                    "elements": "dict",
                    "type": "list",
                    "options": {
                        "route_map": {"type": "str"},
                        "metric": {"type": "int"},
                        "protocol": {
                            "type": "str",
                            "choices": [
                                "connected",
                                "kernel",
                                "ospf",
                                "rip",
                                "static",
                            ],
                        },
                    },
                },
                "network": {
                    "elements": "dict",
                    "type": "list",
                    "options": {
                        "backdoor": {"type": "bool"},
                        "route_map": {"type": "str"},
                        "address": {"type": "str"},
                    },
                },
                "maximum_paths": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "path": {"type": "str"},
                        "count": {"type": "int"},
                    },
                },
                "aggregate_address": {
                    "elements": "dict",
                    "type": "list",
                    "options": {
                        "summary_only": {"type": "bool"},
                        "as_set": {"type": "bool"},
                        "prefix": {"type": "str"},
                    },
                },
                "timers": {
                    "type": "dict",
                    "options": {
                        "holdtime": {"type": "int"},
                        "keepalive": {"type": "int"},
                    },
                },
                "neighbor": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "shutdown": {"type": "bool"},
                        "weight": {"type": "int"},
                        "default_originate": {"type": "str"},
                        "peer_group_name": {"type": "str"},
                        "route_reflector_client": {"type": "bool"},
                        "strict_capability_match": {"type": "bool"},
                        "remove_private_as": {"type": "bool"},
                        "as_override": {"type": "bool"},
                        "port": {"type": "int"},
                        "soft_reconfiguration": {"type": "bool"},
                        "nexthop_self": {"type": "bool"},
                        "remote_as": {"type": "int"},
                        "ebgp_multihop": {"type": "int"},
                        "route_map": {
                            "elements": "dict",
                            "type": "list",
                            "options": {
                                "action": {
                                    "type": "str",
                                    "choices": ["export", "import"],
                                },
                                "route_map": {"type": "str"},
                            },
                        },
                        "distribute_list": {
                            "elements": "dict",
                            "type": "list",
                            "options": {
                                "action": {
                                    "type": "str",
                                    "choices": ["export", "import"],
                                },
                                "acl": {"type": "int"},
                            },
                        },
                        "allowas_in": {"type": "int"},
                        "passive": {"type": "bool"},
                        "ttl_security": {"type": "int"},
                        "peer_group": {"type": "bool"},
                        "maximum_prefix": {"type": "int"},
                        "prefix_list": {
                            "elements": "dict",
                            "type": "list",
                            "options": {
                                "action": {
                                    "type": "str",
                                    "choices": ["export", "import"],
                                },
                                "prefix_list": {"type": "str"},
                            },
                        },
                        "update_source": {"type": "str"},
                        "description": {"type": "str"},
                        "local_as": {"type": "int"},
                        "route_server_client": {"type": "bool"},
                        "attribute_unchanged": {
                            "type": "dict",
                            "options": {
                                "as_path": {"type": "bool"},
                                "med": {"type": "bool"},
                                "next_hop": {"type": "bool"},
                            },
                        },
                        "disable_connected_check": {"type": "bool"},
                        "address": {"type": "str"},
                        "password": {"type": "str", "no_log": True},
                        "disable_send_community": {
                            "type": "str",
                            "choices": ["extended", "standard"],
                        },
                        "unsuppress_map": {"type": "str"},
                        "override_capability": {"type": "bool"},
                        "filter_list": {
                            "elements": "dict",
                            "type": "list",
                            "options": {
                                "action": {
                                    "type": "str",
                                    "choices": ["export", "import"],
                                },
                                "path_list": {"type": "str"},
                            },
                        },
                        "capability": {
                            "type": "dict",
                            "options": {
                                "orf": {
                                    "type": "str",
                                    "choices": ["send", "receive"],
                                },
                                "dynamic": {"type": "bool"},
                            },
                        },
                        "timers": {
                            "type": "dict",
                            "options": {
                                "holdtime": {"type": "int"},
                                "connect": {"type": "int"},
                                "keepalive": {"type": "int"},
                            },
                        },
                        "disable_capability_negotiation": {"type": "bool"},
                        "advertisement_interval": {"type": "int"},
                    },
                },
                "bgp_params": {
                    "type": "dict",
                    "options": {
                        "router_id": {"type": "str"},
                        "distance": {
                            "elements": "dict",
                            "type": "list",
                            "options": {
                                "prefix": {"type": "int"},
                                "type": {
                                    "type": "str",
                                    "choices": [
                                        "external",
                                        "internal",
                                        "local",
                                    ],
                                },
                                "value": {"type": "int"},
                            },
                        },
                        "dampening": {
                            "type": "dict",
                            "options": {
                                "half_life": {"type": "int"},
                                "start_suppress_time": {"type": "int"},
                                "max_suppress_time": {"type": "int"},
                                "re_use": {"type": "int"},
                            },
                        },
                        "graceful_restart": {"type": "int"},
                        "scan_time": {"type": "int"},
                        "always_compare_med": {"type": "bool"},
                        "no_fast_external_failover": {"type": "bool"},
                        "bestpath": {
                            "type": "dict",
                            "options": {
                                "med": {
                                    "type": "str",
                                    "choices": ["confed", "missing-as-worst"],
                                },
                                "as_path": {
                                    "type": "str",
                                    "choices": ["confed", "ignore"],
                                },
                                "compare_routerid": {"type": "bool"},
                            },
                        },
                        "enforce_first_as": {"type": "bool"},
                        "default": {
                            "type": "dict",
                            "options": {
                                "local_pref": {"type": "int"},
                                "no_ipv4_unicast": {"type": "bool"},
                            },
                        },
                        "cluster_id": {"type": "str"},
                        "no_client_to_client_reflection": {"type": "bool"},
                        "deterministic_med": {"type": "bool"},
                        "log_neighbor_changes": {"type": "bool"},
                        "disable_network_import_check": {"type": "bool"},
                        "confederation": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "peers": {"type": "int"},
                                "identifier": {"type": "int"},
                            },
                        },
                    },
                },
                "as_number": {"type": "int"},
            },
        },
    }  # pylint: disable=C0301
