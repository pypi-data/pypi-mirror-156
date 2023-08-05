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
The arg spec for the eos_route_maps module
"""


class Route_mapsArgs(object):  # pylint: disable=R0903
    """The arg spec for the eos_route_maps module"""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "running_config": {"type": "str"},
        "state": {
            "default": "merged",
            "type": "str",
            "choices": [
                "deleted",
                "merged",
                "overridden",
                "replaced",
                "gathered",
                "rendered",
                "parsed",
            ],
        },
        "config": {
            "elements": "dict",
            "type": "list",
            "options": {
                "route_map": {"type": "str"},
                "entries": {
                    "elements": "dict",
                    "type": "list",
                    "options": {
                        "set": {
                            "type": "dict",
                            "options": {
                                "extcommunity": {
                                    "type": "dict",
                                    "options": {
                                        "rt": {
                                            "type": "dict",
                                            "options": {
                                                "vpn": {"type": "str"},
                                                "additive": {"type": "bool"},
                                                "delete": {"type": "bool"},
                                            },
                                        },
                                        "none": {"type": "bool"},
                                        "soo": {
                                            "type": "dict",
                                            "options": {
                                                "vpn": {"type": "str"},
                                                "additive": {"type": "bool"},
                                                "delete": {"type": "bool"},
                                            },
                                        },
                                        "lbw": {
                                            "type": "dict",
                                            "options": {
                                                "aggregate": {"type": "bool"},
                                                "divide": {
                                                    "type": "str",
                                                    "choices": [
                                                        "equal",
                                                        "ration",
                                                    ],
                                                },
                                                "value": {"type": "str"},
                                            },
                                        },
                                    },
                                },
                                "origin": {
                                    "type": "str",
                                    "choices": ["egp", "igp", "incomplete"],
                                },
                                "isis_level": {"type": "str"},
                                "weight": {"type": "int"},
                                "distance": {"type": "int"},
                                "ip": {
                                    "type": "dict",
                                    "options": {
                                        "peer_address": {"type": "bool"},
                                        "unchanged": {"type": "bool"},
                                        "address": {"type": "str"},
                                    },
                                },
                                "metric": {
                                    "type": "dict",
                                    "options": {
                                        "add": {
                                            "type": "str",
                                            "choices": [
                                                "igp-metric",
                                                "igp-nexthop-cost",
                                            ],
                                        },
                                        "igp_param": {
                                            "type": "str",
                                            "choices": [
                                                "igp-metric",
                                                "igp-nexthop-cost",
                                            ],
                                        },
                                        "value": {"type": "str"},
                                    },
                                },
                                "nexthop": {
                                    "type": "dict",
                                    "options": {
                                        "value": {"type": "int"},
                                        "max_metric": {"type": "bool"},
                                    },
                                },
                                "as_path": {
                                    "type": "dict",
                                    "options": {
                                        "match": {
                                            "type": "dict",
                                            "options": {
                                                "as_number": {"type": "str"},
                                                "none": {"type": "bool"},
                                            },
                                        },
                                        "prepend": {
                                            "type": "dict",
                                            "options": {
                                                "last_as": {"type": "int"},
                                                "as_number": {"type": "str"},
                                            },
                                        },
                                    },
                                },
                                "community_attributes": {
                                    "type": "dict",
                                    "options": {
                                        "none": {"type": "bool"},
                                        "graceful_shutdown": {"type": "bool"},
                                        "community": {
                                            "type": "dict",
                                            "options": {
                                                "additive": {"type": "bool"},
                                                "local_as": {"type": "bool"},
                                                "no_export": {"type": "bool"},
                                                "list": {"type": "str"},
                                                "number": {"type": "str"},
                                                "no_advertise": {
                                                    "type": "bool"
                                                },
                                                "internet": {"type": "bool"},
                                                "graceful_shutdown": {
                                                    "type": "bool"
                                                },
                                                "delete": {"type": "bool"},
                                            },
                                        },
                                    },
                                },
                                "bgp": {"type": "int"},
                                "tag": {"type": "int"},
                                "local_preference": {"type": "int"},
                                "segment_index": {"type": "int"},
                                "ipv6": {
                                    "type": "dict",
                                    "options": {
                                        "peer_address": {"type": "bool"},
                                        "unchanged": {"type": "bool"},
                                        "address": {"type": "str"},
                                    },
                                },
                                "metric_type": {
                                    "type": "str",
                                    "choices": ["type-1", "type-2"],
                                },
                                "evpn": {"type": "bool"},
                            },
                        },
                        "description": {"type": "str"},
                        "sequence": {"type": "int"},
                        "source": {"type": "dict"},
                        "continue_sequence": {"type": "int"},
                        "statement": {"type": "str"},
                        "action": {
                            "type": "str",
                            "choices": ["deny", "permit"],
                        },
                        "sub_route_map": {
                            "type": "dict",
                            "options": {
                                "name": {"type": "str"},
                                "invert_result": {"type": "bool"},
                            },
                        },
                        "match": {
                            "type": "dict",
                            "options": {
                                "extcommunity": {
                                    "type": "dict",
                                    "options": {
                                        "community_list": {"type": "str"},
                                        "exact_match": {"type": "bool"},
                                    },
                                },
                                "router_id": {"type": "str"},
                                "invert_result": {
                                    "type": "dict",
                                    "options": {
                                        "extcommunity": {
                                            "type": "dict",
                                            "options": {
                                                "community_list": {
                                                    "type": "str"
                                                },
                                                "exact_match": {
                                                    "type": "bool"
                                                },
                                            },
                                        },
                                        "large_community": {
                                            "type": "dict",
                                            "options": {
                                                "community_list": {
                                                    "type": "str"
                                                },
                                                "exact_match": {
                                                    "type": "bool"
                                                },
                                            },
                                        },
                                        "aggregate_role": {
                                            "type": "dict",
                                            "options": {
                                                "contributor": {
                                                    "type": "bool"
                                                },
                                                "route_map": {"type": "str"},
                                            },
                                        },
                                        "as_path": {
                                            "type": "dict",
                                            "options": {
                                                "path_list": {"type": "str"},
                                                "length": {"type": "str"},
                                            },
                                        },
                                        "community": {
                                            "type": "dict",
                                            "options": {
                                                "community_list": {
                                                    "type": "str"
                                                },
                                                "instances": {"type": "str"},
                                                "exact_match": {
                                                    "type": "bool"
                                                },
                                            },
                                        },
                                    },
                                },
                                "large_community": {
                                    "type": "dict",
                                    "options": {
                                        "community_list": {"type": "str"},
                                        "exact_match": {"type": "bool"},
                                    },
                                },
                                "ip": {
                                    "type": "dict",
                                    "options": {
                                        "resolved_next_hop": {"type": "str"},
                                        "next_hop": {"type": "str"},
                                        "address": {
                                            "type": "dict",
                                            "options": {
                                                "prefix_list": {"type": "str"},
                                                "dynamic": {"type": "bool"},
                                                "access_list": {"type": "str"},
                                            },
                                        },
                                    },
                                },
                                "aggregate_role": {
                                    "type": "dict",
                                    "options": {
                                        "contributor": {"type": "bool"},
                                        "route_map": {"type": "str"},
                                    },
                                },
                                "isis_level": {"type": "str"},
                                "community": {
                                    "type": "dict",
                                    "options": {
                                        "community_list": {"type": "str"},
                                        "instances": {"type": "str"},
                                        "exact_match": {"type": "bool"},
                                    },
                                },
                                "as_path": {
                                    "type": "dict",
                                    "options": {
                                        "path_list": {"type": "str"},
                                        "length": {"type": "str"},
                                    },
                                },
                                "route_type": {"type": "str"},
                                "as": {"type": "int"},
                                "tag": {"type": "int"},
                                "local_preference": {"type": "int"},
                                "ipv6": {
                                    "type": "dict",
                                    "options": {
                                        "resolved_next_hop": {"type": "str"},
                                        "next_hop": {"type": "str"},
                                        "address": {
                                            "type": "dict",
                                            "options": {
                                                "prefix_list": {"type": "str"},
                                                "dynamic": {"type": "bool"},
                                                "access_list": {"type": "str"},
                                            },
                                        },
                                    },
                                },
                                "metric_type": {
                                    "type": "str",
                                    "choices": ["type-1", "type-2"],
                                },
                                "interface": {"type": "str"},
                                "source_protocol": {"type": "str"},
                                "metric": {"type": "int"},
                            },
                        },
                    },
                },
            },
        },
    }  # pylint: disable=C0301
