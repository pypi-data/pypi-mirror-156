#
# -*- coding: utf-8 -*-
# Copyright 2019 Cisco and/or its affiliates.
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
The arg spec for the nxos_telemetry module
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type


class TelemetryArgs(object):  # pylint: disable=R0903
    """The arg spec for the nxos_telemetry module"""

    argument_spec = {
        "config": {
            "options": {
                "certificate": {
                    "options": {
                        "hostname": {"type": "str"},
                        "key": {"type": "str", "no_log": False},
                    },
                    "type": "dict",
                },
                "compression": {"choices": ["gzip"], "type": "str"},
                "source_interface": {"type": "str"},
                "vrf": {"type": "str"},
                "destination_groups": {
                    "options": {
                        "destination": {
                            "options": {
                                "encoding": {
                                    "choices": ["GPB", "JSON"],
                                    "type": "str",
                                },
                                "ip": {"type": "str"},
                                "port": {"type": "int"},
                                "protocol": {
                                    "choices": ["HTTP", "TCP", "UDP", "gRPC"],
                                    "type": "str",
                                },
                            },
                            "type": "dict",
                        },
                        "id": {"type": "int"},
                    },
                    "type": "list",
                    "elements": "raw",
                },
                "sensor_groups": {
                    "options": {
                        "data_source": {
                            "choices": ["NX-API", "DME", "YANG"],
                            "type": "str",
                        },
                        "id": {"type": "int"},
                        "path": {
                            "options": {
                                "depth": {"type": "str"},
                                "filter_condition": {"type": "str"},
                                "name": {"type": "str"},
                                "query_condition": {"type": "str"},
                            },
                            "type": "dict",
                        },
                    },
                    "type": "list",
                    "elements": "raw",
                },
                "subscriptions": {
                    "options": {
                        "destination_group": {"type": "int"},
                        "id": {"type": "int"},
                        "sensor_group": {
                            "options": {
                                "id": {"type": "int"},
                                "sample_interval": {"type": "int"},
                            },
                            "type": "dict",
                        },
                    },
                    "type": "list",
                    "elements": "raw",
                },
            },
            "type": "dict",
        },
        "state": {
            "choices": ["merged", "replaced", "deleted", "gathered"],
            "default": "merged",
            "type": "str",
        },
    }  # pylint: disable=C0301
