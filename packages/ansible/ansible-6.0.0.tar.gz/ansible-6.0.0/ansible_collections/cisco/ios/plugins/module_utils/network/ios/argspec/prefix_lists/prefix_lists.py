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
# This file is auto generated by the
# cli_rm_builder.
#
# Manually editing this file is not advised.
#
# To update the argspec make the desired changes
# in the module docstring and re-run
# cli_rm_builder.
#
#############################################

"""
The arg spec for the cisco.ios_prefix_lists module
"""


class Prefix_listsArgs(object):
    """The arg spec for the cisco.ios_prefix_lists module"""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "afi": {"type": "str", "choices": ["ipv4", "ipv6"]},
                "prefix_lists": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {"type": "str"},
                        "description": {"type": "str"},
                        "entries": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "action": {
                                    "type": "str",
                                    "choices": ["deny", "permit"],
                                },
                                "sequence": {"type": "int"},
                                "description": {"type": "str"},
                                "prefix": {"type": "str"},
                                "ge": {"type": "int"},
                                "le": {"type": "int"},
                            },
                        },
                    },
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "parsed",
                "rendered",
            ],
            "default": "merged",
        },
    }
