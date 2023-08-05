# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat
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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.junipernetworks.junos.tests.unit.compat.mock import (
    patch,
)
from ansible_collections.junipernetworks.junos.plugins.modules import (
    junos_security_policies_global,
)
from ansible_collections.junipernetworks.junos.tests.unit.modules.utils import (
    set_module_args,
)
from .junos_module import TestJunosModule, load_fixture


class TestJunosSecurity_policies_globalModule(TestJunosModule):
    module = junos_security_policies_global

    def setUp(self):
        super(TestJunosSecurity_policies_globalModule, self).setUp()

        self.mock_lock_configuration = patch(
            "ansible_collections.junipernetworks.junos.plugins.module_utils.network.junos.junos.lock_configuration"
        )
        self.lock_configuration = self.mock_lock_configuration.start()

        self.mock_unlock_configuration = patch(
            "ansible_collections.junipernetworks.junos.plugins.module_utils.network.junos.junos.unlock_configuration"
        )
        self.unlock_configuration = self.mock_unlock_configuration.start()

        self.mock_load_config = patch(
            "ansible_collections.junipernetworks.junos.plugins.module_utils.network.junos.config.security_policies_global.security_policies_global.load_config"
        )
        self.load_config = self.mock_load_config.start()

        self.mock_commit_configuration = patch(
            "ansible_collections.junipernetworks.junos.plugins.module_utils.network.junos.config.security_policies_global."
            "security_policies_global.commit_configuration"
        )
        self.mock_commit_configuration = self.mock_commit_configuration.start()

        self.mock_execute_show_command = patch(
            "ansible_collections.junipernetworks.junos.plugins.module_utils.network.junos.facts.security_policies_global.security_policies_global."
            "Security_policies_globalFacts._get_device_data"
        )
        self.execute_show_command = self.mock_execute_show_command.start()
        self.maxDiff = None

    def tearDown(self):
        super(TestJunosSecurity_policies_globalModule, self).tearDown()
        self.mock_load_config.stop()
        self.mock_lock_configuration.stop()
        self.mock_unlock_configuration.stop()
        self.mock_commit_configuration.stop()
        self.mock_execute_show_command.stop()

    def load_fixtures(
        self, commands=None, format="text", changed=False, filename=None
    ):
        def load_from_file(*args, **kwargs):
            output = load_fixture("junos_security_policies_global_config.cfg")
            return output

        self.execute_show_command.side_effect = load_from_file

    def sorted_xml(self, xml_string):
        temp = []
        index = 0
        while index < len(xml_string):
            temp_line = ""
            if xml_string[index] == "<":
                while index < len(xml_string) and xml_string[index] != ">":
                    temp_line += xml_string[index]
                    index += 1
                temp_line += ">"
                index += 1
                temp.append(temp_line)
            else:
                while index < len(xml_string) and xml_string[index] != "<":
                    temp_line += xml_string[index]
                    index += 1
                temp.append(temp_line)
        return sorted(temp)

    def test_junos_security_policies_global_merged_01(self):
        set_module_args(
            dict(
                config={
                    "default_policy": "permit-all",
                    "policy_rematch": {"enable": True, "extensive": True},
                    "policy_stats": {"enable": True, "system_wide": True},
                    "pre_id_default_policy_action": {
                        "log": {"session_init": True, "session_close": True},
                        "session_timeout": {"icmp": 10, "others": 10},
                    },
                    "traceoptions": {
                        "file": {
                            "files": 3,
                            "match": "/[A-Z]*/gm",
                            "no_world_readable": True,
                            "size": "10k",
                        },
                        "flag": "all",
                        "no_remote_trace": True,
                    },
                },
                state="merged",
            )
        )
        result = self.execute_module(changed=True)
        commands = (
            '<nc:security xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><nc:policies>'
            "<nc:default-policy><nc:permit-all/></nc:default-policy><nc:policy-rematch> <nc:extensive/>"
            "</nc:policy-rematch><nc:policy-stats> <nc:system-wide>enable</nc:system-wide></nc:policy-stats>"
            "<nc:pre-id-default-policy><nc:then><nc:log><nc:session-init/><nc:session-close/></nc:log><nc:session-timeout>"
            "<nc:icmp>10</nc:icmp><nc:others>10</nc:others></nc:session-timeout></nc:then>"
            "</nc:pre-id-default-policy><nc:traceoptions><nc:file><nc:files>3</nc:files><nc:match>"
            "/[A-Z]*/gm</nc:match><nc:size>10k</nc:size><nc:no-world-readable/></nc:file><nc:flag>"
            "<nc:name>all</nc:name></nc:flag><nc:no-remote-trace/></nc:traceoptions></nc:policies>"
            "</nc:security>"
        )
        self.assertEqual(
            self.sorted_xml(commands), self.sorted_xml(str(result["commands"]))
        )

    def test_junos_security_policies_global_merged_02(self):
        set_module_args(
            dict(
                config={
                    "default_policy": "deny-all",
                    "policy_rematch": {"enable": True, "extensive": True},
                    "policy_stats": {"enable": True, "system_wide": False},
                    "pre_id_default_policy_action": {
                        "log": {"session_init": True},
                        "session_timeout": {
                            "icmp": 10,
                            "others": 10,
                            "icmp6": 10,
                            "ospf": 10,
                            "tcp": 10,
                            "udp": 10,
                        },
                    },
                    "traceoptions": {
                        "file": {
                            "files": 3,
                            "match": "/[A-Z]*/gm",
                            "world_readable": True,
                            "size": "10k",
                        },
                        "flag": "configuration",
                        "no_remote_trace": True,
                    },
                },
                state="merged",
            )
        )
        result = self.execute_module(changed=True)
        commands = (
            '<nc:security xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><nc:policies>'
            "<nc:default-policy><nc:deny-all/></nc:default-policy><nc:policy-rematch> <nc:extensive/>"
            "</nc:policy-rematch><nc:policy-stats> <nc:system-wide>disable</nc:system-wide></nc:policy-stats>"
            "<nc:pre-id-default-policy><nc:then><nc:log><nc:session-init/></nc:log><nc:session-timeout>"
            "<nc:icmp>10</nc:icmp><nc:others>10</nc:others><nc:icmp6>10</nc:icmp6><nc:ospf>10</nc:ospf>"
            "<nc:tcp>10</nc:tcp><nc:udp>10</nc:udp></nc:session-timeout></nc:then></nc:pre-id-default-policy>"
            "<nc:traceoptions><nc:file><nc:files>3</nc:files><nc:match>/[A-Z]*/gm</nc:match><nc:size>10k</nc:size>"
            "<nc:world-readable/></nc:file><nc:flag><nc:name>configuration</nc:name></nc:flag><nc:no-remote-trace/>"
            "</nc:traceoptions></nc:policies></nc:security>"
        )
        self.assertEqual(
            self.sorted_xml(commands), self.sorted_xml(str(result["commands"]))
        )

    def test_junos_security_policies_global_merged_03(self):
        set_module_args(
            dict(
                config={"traceoptions": {"flag": "compilation"}},
                state="merged",
            )
        )
        result = self.execute_module(changed=True)
        commands = (
            '<nc:security xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><nc:policies>'
            "<nc:traceoptions><nc:flag><nc:name>compilation</nc:name></nc:flag>"
            "</nc:traceoptions></nc:policies></nc:security>"
        )
        self.assertEqual(
            self.sorted_xml(commands), self.sorted_xml(str(result["commands"]))
        )

    def test_junos_security_policies_global_merged_04(self):
        set_module_args(
            dict(config={"traceoptions": {"flag": "lookup"}}, state="merged")
        )
        result = self.execute_module(changed=True)
        commands = (
            '<nc:security xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><nc:policies>'
            "<nc:traceoptions><nc:flag><nc:name>lookup</nc:name></nc:flag>"
            "</nc:traceoptions></nc:policies></nc:security>"
        )
        self.assertEqual(
            self.sorted_xml(commands), self.sorted_xml(str(result["commands"]))
        )

    def test_junos_security_policies_global_parsed_01(self):
        parsed_str = """
            <rpc-reply message-id="urn:uuid:0cadb4e8-5bba-47f4-986e-72906227007f">
                <configuration changed-seconds="1590139550" changed-localtime="2020-05-22 09:25:50 UTC">
                    <version>18.4R1-S2.4</version>
                    <security>
                        <policies>
                            <traceoptions>
                                <no-remote-trace />
                                <file>
                                    <size>10k</size>
                                    <files>3</files>
                                    <no-world-readable />
                                    <match>/[A-Z]*/gm</match>
                                </file>
                                <flag>
                                    <name>all</name>
                                </flag>
                            </traceoptions>
                            <default-policy>
                                <permit-all />
                            </default-policy>
                            <policy-rematch>
                                <extensive />
                            </policy-rematch>
                            <policy-stats>
                                <system-wide>enable</system-wide>
                            </policy-stats>
                            <pre-id-default-policy>
                                <then>
                                    <log>
                                        <session-init />
                                    </log>
                                    <session-timeout>
                                        <icmp>10</icmp>
                                        <others>10</others>
                                    </session-timeout>
                                </then>
                            </pre-id-default-policy>
                        </policies>
                    </security>
                </configuration>
            </rpc-reply>
        """
        set_module_args(dict(running_config=parsed_str, state="parsed"))
        result = self.execute_module(changed=False)
        parsed_dict = {
            "default_policy": "permit-all",
            "policy_rematch": {"enable": True, "extensive": True},
            "policy_stats": {"enable": True, "system_wide": True},
            "pre_id_default_policy_action": {
                "log": {"session_init": True},
                "session_timeout": {"icmp": 10, "others": 10},
            },
            "traceoptions": {
                "file": {
                    "files": 3,
                    "match": "/[A-Z]*/gm",
                    "no_world_readable": True,
                    "size": "10k",
                },
                "flag": "compilation",
                "no_remote_trace": True,
            },
        }
        self.assertEqual(sorted(parsed_dict), sorted(result["parsed"]))

    def test_junos_security_policies_global_parsed_02(self):
        parsed_str = """
            <rpc-reply message-id="urn:uuid:0cadb4e8-5bba-47f4-986e-72906227007f">
                <configuration changed-seconds="1590139550" changed-localtime="2020-05-22 09:25:50 UTC">
                    <version>18.4R1-S2.4</version>
                    <security>
                        <policies>
                            <traceoptions>
                                <file>
                                    <size>10k</size>
                                    <files>3</files>
                                    <world-readable />
                                    <match>/[A-Z]*/gm</match>
                                </file>
                                <flag>
                                    <name>compilation</name>
                                </flag>
                            </traceoptions>
                            <default-policy>
                                <deny-all />
                            </default-policy>
                            <policy-stats>
                                <system-wide>disable</system-wide>
                            </policy-stats>
                            <pre-id-default-policy>
                                <then>
                                    <log>
                                        <session-close />
                                    </log>
                                    <session-timeout>
                                        <icmp>10</icmp>
                                        <others>10</others>
                                        <icmp6>10</icmp6>
                                        <ospf>10</ospf>
                                        <tcp>10</tcp>
                                        <udp>10</udp>
                                    </session-timeout>
                                </then>
                            </pre-id-default-policy>
                        </policies>
                    </security>
                </configuration>
            </rpc-reply>
        """
        set_module_args(dict(running_config=parsed_str, state="parsed"))
        result = self.execute_module(changed=False)
        parsed_dict = {
            "default_policy": "deny-all",
            "policy_stats": {"enable": True, "system_wide": False},
            "pre_id_default_policy_action": {
                "log": {"session_close": True},
                "session_timeout": {
                    "icmp": 10,
                    "others": 10,
                    "ospf": 10,
                    "icmp6": 10,
                    "tcp": 10,
                    "udp": 10,
                },
            },
            "traceoptions": {
                "file": {
                    "files": 3,
                    "match": "/[A-Z]*/gm",
                    "world_readable": True,
                    "size": "10k",
                },
                "flag": "compilation",
            },
        }
        self.assertEqual(sorted(parsed_dict), sorted(result["parsed"]))

    def test_junos_security_policies_global_parsed_03(self):
        parsed_str = """
            <rpc-reply message-id="urn:uuid:0cadb4e8-5bba-47f4-986e-72906227007f">
                <configuration changed-seconds="1590139550" changed-localtime="2020-05-22 09:25:50 UTC">
                    <version>18.4R1-S2.4</version>
                    <security>
                        <policies>
                            <traceoptions>
                                <flag>
                                    <name>configuration</name>
                                </flag>
                            </traceoptions>
                        </policies>
                    </security>
                </configuration>
            </rpc-reply>
        """
        set_module_args(dict(running_config=parsed_str, state="parsed"))
        result = self.execute_module(changed=False)
        parsed_dict = {"traceoptions": {"flag": "configuration"}}
        self.assertEqual(sorted(parsed_dict), sorted(result["parsed"]))

    def test_junos_security_policies_global_parsed_04(self):
        parsed_str = """
            <rpc-reply message-id="urn:uuid:0cadb4e8-5bba-47f4-986e-72906227007f">
                <configuration changed-seconds="1590139550" changed-localtime="2020-05-22 09:25:50 UTC">
                    <version>18.4R1-S2.4</version>
                    <security>
                        <policies>
                            <traceoptions>
                                <flag>
                                    <name>ipc</name>
                                </flag>
                            </traceoptions>
                        </policies>
                    </security>
                </configuration>
            </rpc-reply>
        """
        set_module_args(dict(running_config=parsed_str, state="parsed"))
        result = self.execute_module(changed=False)
        parsed_dict = {"traceoptions": {"flag": "ipc"}}
        self.assertEqual(sorted(parsed_dict), sorted(result["parsed"]))

    def test_junos_security_policies_global_parsed_05(self):
        parsed_str = """
            <rpc-reply message-id="urn:uuid:0cadb4e8-5bba-47f4-986e-72906227007f">
                <configuration changed-seconds="1590139550" changed-localtime="2020-05-22 09:25:50 UTC">
                    <version>18.4R1-S2.4</version>
                    <security>
                        <policies>
                            <traceoptions>
                                <flag>
                                    <name>lookup</name>
                                </flag>
                            </traceoptions>
                        </policies>
                    </security>
                </configuration>
            </rpc-reply>
        """
        set_module_args(dict(running_config=parsed_str, state="parsed"))
        result = self.execute_module(changed=False)
        parsed_dict = {"traceoptions": {"flag": "lookup"}}
        self.assertEqual(sorted(parsed_dict), sorted(result["parsed"]))

    def test_junos_security_policies_global_parsed_06(self):
        parsed_str = """
            <rpc-reply message-id="urn:uuid:0cadb4e8-5bba-47f4-986e-72906227007f">
                <configuration changed-seconds="1590139550" changed-localtime="2020-05-22 09:25:50 UTC">
                    <version>18.4R1-S2.4</version>
                    <security>
                        <policies>
                            <traceoptions>
                                <flag>
                                    <name>routing-socket</name>
                                </flag>
                            </traceoptions>
                        </policies>
                    </security>
                </configuration>
            </rpc-reply>
        """
        set_module_args(dict(running_config=parsed_str, state="parsed"))
        result = self.execute_module(changed=False)
        parsed_dict = {"traceoptions": {"flag": "routing-socket"}}
        self.assertEqual(sorted(parsed_dict), sorted(result["parsed"]))

    def test_junos_security_policies_global_parsed_07(self):
        parsed_str = """
            <rpc-reply message-id="urn:uuid:0cadb4e8-5bba-47f4-986e-72906227007f">
                <configuration changed-seconds="1590139550" changed-localtime="2020-05-22 09:25:50 UTC">
                    <version>18.4R1-S2.4</version>
                    <security>
                        <policies>
                            <traceoptions>
                                <flag>
                                    <name>rules</name>
                                </flag>
                            </traceoptions>
                        </policies>
                    </security>
                </configuration>
            </rpc-reply>
        """
        set_module_args(dict(running_config=parsed_str, state="parsed"))
        result = self.execute_module(changed=False)
        parsed_dict = {"traceoptions": {"flag": "rules"}}
        self.assertEqual(sorted(parsed_dict), sorted(result["parsed"]))

    def test_junos_security_policies_global_overridden_01(self):
        set_module_args(
            dict(
                config={
                    "default_policy": "permit-all",
                    "policy_rematch": {"enable": True, "extensive": True},
                    "policy_stats": {"enable": True, "system_wide": True},
                    "pre_id_default_policy_action": {
                        "log": {"session_init": True},
                        "session_timeout": {"icmp": 10, "others": 10},
                    },
                    "traceoptions": {
                        "file": {
                            "files": 3,
                            "match": "/[A-Z]*/gm",
                            "no_world_readable": True,
                            "size": "10k",
                        },
                        "flag": "ipc",
                        "no_remote_trace": True,
                    },
                },
                state="overridden",
            )
        )
        result = self.execute_module(changed=True)
        print(result["commands"])
        commands = (
            '<nc:security xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><nc:policies>'
            "<nc:default-policy><nc:permit-all/></nc:default-policy><nc:policy-rematch> <nc:extensive/>"
            "</nc:policy-rematch><nc:policy-stats> <nc:system-wide>enable</nc:system-wide></nc:policy-stats>"
            "<nc:pre-id-default-policy><nc:then><nc:log><nc:session-init/></nc:log><nc:session-timeout>"
            "<nc:icmp>10</nc:icmp><nc:others>10</nc:others></nc:session-timeout></nc:then>"
            "</nc:pre-id-default-policy><nc:traceoptions><nc:file><nc:files>3</nc:files><nc:match>"
            "/[A-Z]*/gm</nc:match><nc:size>10k</nc:size><nc:no-world-readable/></nc:file><nc:flag>"
            "<nc:name>ipc</nc:name></nc:flag><nc:no-remote-trace/></nc:traceoptions></nc:policies>"
            '</nc:security><nc:policies delete="delete"/>'
        )
        self.assertEqual(
            self.sorted_xml(commands), self.sorted_xml(str(result["commands"]))
        )

    def test_junos_security_policies_global_gathered(self):
        """
        :return:
        """
        set_module_args(dict(state="gathered"))
        result = self.execute_module(changed=False)
        gather_list = {
            "default_policy": "permit-all",
            "policy_rematch": {"enable": True, "extensive": True},
            "policy_stats": {"enable": True, "system_wide": True},
            "pre_id_default_policy_action": {
                "log": {"session_init": True},
                "session_timeout": {"icmp": 10, "others": 10},
            },
            "traceoptions": {
                "file": {
                    "files": 3,
                    "match": "/[A-Z]*/gm",
                    "no_world_readable": True,
                    "size": "10k",
                },
                "flag": "lookup",
                "no_remote_trace": True,
            },
        }
        self.assertEqual(sorted(gather_list), sorted(result["gathered"]))

    def test_junos_security_policies_global_rendered(self):
        set_module_args(
            dict(
                config={
                    "default_policy": "permit-all",
                    "policy_rematch": {"enable": True, "extensive": True},
                    "policy_stats": {"enable": True, "system_wide": True},
                    "pre_id_default_policy_action": {
                        "log": {"session_init": True},
                        "session_timeout": {"icmp": 10, "others": 10},
                    },
                    "traceoptions": {
                        "file": {
                            "files": 3,
                            "match": "/[A-Z]*/gm",
                            "no_world_readable": True,
                            "size": "10k",
                        },
                        "flag": "routing-socket",
                        "no_remote_trace": True,
                    },
                },
                state="rendered",
            )
        )
        rendered = (
            '<nc:security xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><nc:policies>'
            "<nc:default-policy><nc:permit-all/></nc:default-policy><nc:policy-rematch> <nc:extensive/>"
            "</nc:policy-rematch><nc:policy-stats> <nc:system-wide>enable</nc:system-wide></nc:policy-stats>"
            "<nc:pre-id-default-policy><nc:then><nc:log><nc:session-init/></nc:log><nc:session-timeout>"
            "<nc:icmp>10</nc:icmp><nc:others>10</nc:others></nc:session-timeout></nc:then>"
            "</nc:pre-id-default-policy><nc:traceoptions><nc:file><nc:files>3</nc:files><nc:match>"
            "/[A-Z]*/gm</nc:match><nc:size>10k</nc:size><nc:no-world-readable/></nc:file><nc:flag>"
            "<nc:name>routing-socket</nc:name></nc:flag><nc:no-remote-trace/></nc:traceoptions></nc:policies>"
            "</nc:security>"
        )
        result = self.execute_module(changed=False)
        print(self.sorted_xml(result["rendered"]))
        print(self.sorted_xml(rendered))
        self.assertEqual(
            self.sorted_xml(result["rendered"]), self.sorted_xml(rendered)
        )

    def test_junos_security_policies_global_replaced_01(self):
        set_module_args(
            dict(
                config={
                    "default_policy": "permit-all",
                    "policy_rematch": {"enable": True, "extensive": True},
                    "policy_stats": {"enable": True, "system_wide": True},
                    "pre_id_default_policy_action": {
                        "log": {"session_init": True},
                        "session_timeout": {"icmp": 10, "others": 10},
                    },
                    "traceoptions": {
                        "file": {
                            "files": 3,
                            "match": "/[A-Z]*/gm",
                            "no_world_readable": True,
                            "size": "10k",
                        },
                        "flag": "rules",
                        "no_remote_trace": True,
                    },
                },
                state="replaced",
            )
        )
        result = self.execute_module(changed=True)
        commands = (
            '<nc:security xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><nc:policies>'
            "<nc:default-policy><nc:permit-all/></nc:default-policy><nc:policy-rematch> <nc:extensive/>"
            "</nc:policy-rematch><nc:policy-stats> <nc:system-wide>enable</nc:system-wide></nc:policy-stats>"
            "<nc:pre-id-default-policy><nc:then><nc:log><nc:session-init/></nc:log><nc:session-timeout>"
            "<nc:icmp>10</nc:icmp><nc:others>10</nc:others></nc:session-timeout></nc:then>"
            "</nc:pre-id-default-policy><nc:traceoptions><nc:file><nc:files>3</nc:files><nc:match>"
            "/[A-Z]*/gm</nc:match><nc:size>10k</nc:size><nc:no-world-readable/></nc:file><nc:flag>"
            "<nc:name>rules</nc:name></nc:flag><nc:no-remote-trace/></nc:traceoptions></nc:policies>"
            '</nc:security><nc:policies delete="delete"/>'
        )
        self.assertEqual(
            self.sorted_xml(commands), self.sorted_xml(str(result["commands"]))
        )
