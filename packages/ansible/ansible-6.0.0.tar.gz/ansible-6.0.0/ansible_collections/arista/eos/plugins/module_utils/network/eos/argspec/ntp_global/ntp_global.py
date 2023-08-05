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
The arg spec for the eos_ntp_global module
"""


class Ntp_globalArgs(object):  # pylint: disable=R0903
    """The arg spec for the eos_ntp_global module"""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "authenticate": {
                    "type": "dict",
                    "options": {
                        "enable": {"type": "bool"},
                        "servers": {"type": "bool"},
                    },
                },
                "authentication_keys": {
                    "type": "list",
                    "elements": "dict",
                    "no_log": False,
                    "options": {
                        "id": {"type": "int"},
                        "algorithm": {
                            "type": "str",
                            "choices": ["md5", "sha1"],
                        },
                        "encryption": {"type": "int", "choices": [0, 7]},
                        "key": {"type": "str", "no_log": True},
                    },
                },
                "local_interface": {"type": "str"},
                "qos_dscp": {"type": "int"},
                "serve": {
                    "type": "dict",
                    "options": {
                        "all": {"type": "bool"},
                        "access_lists": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "afi": {"type": "str"},
                                "acls": {
                                    "type": "list",
                                    "elements": "dict",
                                    "options": {
                                        "acl_name": {"type": "str"},
                                        "direction": {
                                            "type": "str",
                                            "choices": ["in", "out"],
                                        },
                                        "vrf": {"type": "str"},
                                    },
                                },
                            },
                        },
                    },
                },
                "servers": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "vrf": {"type": "str"},
                        "server": {"type": "str", "required": True},
                        "burst": {"type": "bool"},
                        "iburst": {"type": "bool"},
                        "key_id": {"type": "int"},
                        "local_interface": {"type": "str"},
                        "source": {"type": "str"},
                        "maxpoll": {"type": "int"},
                        "minpoll": {"type": "int"},
                        "prefer": {"type": "bool"},
                        "version": {"type": "int"},
                    },
                },
                "trusted_key": {"type": "str", "no_log": False},
            },
        },
        "running_config": {"type": "str"},
        "state": {
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
            "default": "merged",
        },
    }  # pylint: disable=C0301
