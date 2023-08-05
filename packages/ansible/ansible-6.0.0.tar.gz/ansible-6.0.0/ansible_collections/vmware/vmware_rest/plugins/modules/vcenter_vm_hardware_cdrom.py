#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# template: header.j2
# This module is autogenerated by vmware_rest_code_generator.
# See: https://github.com/ansible-collections/vmware_rest_code_generator
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: vcenter_vm_hardware_cdrom
short_description: Adds a virtual CD-ROM device to the virtual machine.
description: Adds a virtual CD-ROM device to the virtual machine.
options:
  allow_guest_control:
    description:
    - Flag indicating whether the guest can connect and disconnect the device.
    type: bool
  backing:
    description:
    - Physical resource backing for the virtual CD-ROM device. Required with I(state=['present'])
    - 'Valid attributes are:'
    - ' - C(type) (str): The C(backing_type) defines the valid backing types for a
      virtual CD-ROM device. ([''present''])'
    - '   This key is required with [''present''].'
    - '   - Accepted values:'
    - '     - CLIENT_DEVICE'
    - '     - HOST_DEVICE'
    - '     - ISO_FILE'
    - ' - C(iso_file) (str): Path of the image file that should be used as the virtual
      CD-ROM device backing. ([''present''])'
    - ' - C(host_device) (str): Name of the device that should be used as the virtual
      CD-ROM device backing. ([''present''])'
    - ' - C(device_access_type) (str): The C(device_access_type) defines the valid
      device access types for a physical device packing of a virtual CD-ROM device.
      ([''present''])'
    - '   - Accepted values:'
    - '     - EMULATION'
    - '     - PASSTHRU'
    - '     - PASSTHRU_EXCLUSIVE'
    type: dict
  cdrom:
    description:
    - Virtual CD-ROM device identifier. Required with I(state=['absent', 'connect',
      'disconnect', 'present'])
    type: str
  ide:
    description:
    - Address for attaching the device to a virtual IDE adapter.
    - 'Valid attributes are:'
    - ' - C(primary) (bool): Flag specifying whether the device should be attached
      to the primary or secondary IDE adapter of the virtual machine. ([''present''])'
    - ' - C(master) (bool): Flag specifying whether the device should be the master
      or slave device on the IDE adapter. ([''present''])'
    type: dict
  label:
    description:
    - The name of the item
    type: str
  sata:
    description:
    - Address for attaching the device to a virtual SATA adapter. Required with I(state=['present'])
    - 'Valid attributes are:'
    - ' - C(bus) (int): Bus number of the adapter to which the device should be attached.
      ([''present''])'
    - '   This key is required with [''present''].'
    - ' - C(unit) (int): Unit number of the device. ([''present''])'
    type: dict
  session_timeout:
    description:
    - 'Timeout settings for client session. '
    - 'The maximal number of seconds for the whole operation including connection
      establishment, request sending and response. '
    - The default value is 300s.
    type: float
    version_added: 2.1.0
  start_connected:
    description:
    - Flag indicating whether the virtual device should be connected whenever the
      virtual machine is powered on.
    type: bool
  state:
    choices:
    - absent
    - connect
    - disconnect
    - present
    default: present
    description: []
    type: str
  type:
    choices:
    - IDE
    - SATA
    description:
    - The C(host_bus_adapter_type) defines the valid types of host bus adapters that
      may be used for attaching a Cdrom to a virtual machine.
    type: str
  vcenter_hostname:
    description:
    - The hostname or IP address of the vSphere vCenter
    - If the value is not specified in the task, the value of environment variable
      C(VMWARE_HOST) will be used instead.
    required: true
    type: str
  vcenter_password:
    description:
    - The vSphere vCenter password
    - If the value is not specified in the task, the value of environment variable
      C(VMWARE_PASSWORD) will be used instead.
    required: true
    type: str
  vcenter_rest_log_file:
    description:
    - 'You can use this optional parameter to set the location of a log file. '
    - 'This file will be used to record the HTTP REST interaction. '
    - 'The file will be stored on the host that run the module. '
    - 'If the value is not specified in the task, the value of '
    - environment variable C(VMWARE_REST_LOG_FILE) will be used instead.
    type: str
  vcenter_username:
    description:
    - The vSphere vCenter username
    - If the value is not specified in the task, the value of environment variable
      C(VMWARE_USER) will be used instead.
    required: true
    type: str
  vcenter_validate_certs:
    default: true
    description:
    - Allows connection when SSL certificates are not valid. Set to C(false) when
      certificates are not trusted.
    - If the value is not specified in the task, the value of environment variable
      C(VMWARE_VALIDATE_CERTS) will be used instead.
    type: bool
  vm:
    description:
    - Virtual machine identifier. This parameter is mandatory.
    required: true
    type: str
author:
- Ansible Cloud Team (@ansible-collections)
version_added: 0.1.0
requirements:
- vSphere 7.0.2 or greater
- python >= 3.6
- aiohttp
notes:
- Tested on vSphere 7.0.2
"""

EXAMPLES = r"""
- name: Look up the VM called test_vm1 in the inventory
  register: search_result
  vmware.vmware_rest.vcenter_vm_info:
    filter_names:
    - test_vm1

- name: Collect information about a specific VM
  vmware.vmware_rest.vcenter_vm_info:
    vm: '{{ search_result.value[0].vm }}'
  register: test_vm1_info

- name: Attach an ISO image to a guest VM
  vmware.vmware_rest.vcenter_vm_hardware_cdrom:
    vm: '{{ test_vm1_info.id }}'
    type: SATA
    sata:
      bus: 0
      unit: 2
    start_connected: true
    backing:
      iso_file: '[ro_datastore] fedora.iso'
      type: ISO_FILE
"""

RETURN = r"""
# content generated by the update_return_section callback# task: Attach an ISO image to a guest VM
id:
  description: moid of the resource
  returned: On success
  sample: '16002'
  type: str
value:
  description: Attach an ISO image to a guest VM
  returned: On success
  sample:
    allow_guest_control: 0
    backing:
      iso_file: '[ro_datastore] fedora.iso'
      type: ISO_FILE
    label: CD/DVD drive 1
    sata:
      bus: 0
      unit: 2
    start_connected: 1
    state: NOT_CONNECTED
    type: SATA
  type: dict
"""

# This structure describes the format of the data expected by the end-points
PAYLOAD_FORMAT = {
    "delete": {"query": {}, "body": {}, "path": {"cdrom": "cdrom", "vm": "vm"}},
    "update": {
        "query": {},
        "body": {
            "allow_guest_control": "allow_guest_control",
            "backing": "backing",
            "start_connected": "start_connected",
        },
        "path": {"cdrom": "cdrom", "vm": "vm"},
    },
    "connect": {"query": {}, "body": {}, "path": {"cdrom": "cdrom", "vm": "vm"}},
    "disconnect": {"query": {}, "body": {}, "path": {"cdrom": "cdrom", "vm": "vm"}},
    "create": {
        "query": {},
        "body": {
            "allow_guest_control": "allow_guest_control",
            "backing": "backing",
            "ide": "ide",
            "sata": "sata",
            "start_connected": "start_connected",
            "type": "type",
        },
        "path": {"vm": "vm"},
    },
}  # pylint: disable=line-too-long

import json
import socket
from ansible.module_utils.basic import env_fallback

try:
    from ansible_collections.cloud.common.plugins.module_utils.turbo.exceptions import (
        EmbeddedModuleFailure,
    )
    from ansible_collections.cloud.common.plugins.module_utils.turbo.module import (
        AnsibleTurboModule as AnsibleModule,
    )

    AnsibleModule.collection_name = "vmware.vmware_rest"
except ImportError:
    from ansible.module_utils.basic import AnsibleModule
from ansible_collections.vmware.vmware_rest.plugins.module_utils.vmware_rest import (
    build_full_device_list,
    exists,
    gen_args,
    get_device_info,
    get_subdevice_type,
    list_devices,
    open_session,
    prepare_payload,
    update_changed_flag,
    session_timeout,
)


def prepare_argument_spec():
    argument_spec = {
        "vcenter_hostname": dict(
            type="str", required=True, fallback=(env_fallback, ["VMWARE_HOST"]),
        ),
        "vcenter_username": dict(
            type="str", required=True, fallback=(env_fallback, ["VMWARE_USER"]),
        ),
        "vcenter_password": dict(
            type="str",
            required=True,
            no_log=True,
            fallback=(env_fallback, ["VMWARE_PASSWORD"]),
        ),
        "vcenter_validate_certs": dict(
            type="bool",
            required=False,
            default=True,
            fallback=(env_fallback, ["VMWARE_VALIDATE_CERTS"]),
        ),
        "vcenter_rest_log_file": dict(
            type="str",
            required=False,
            fallback=(env_fallback, ["VMWARE_REST_LOG_FILE"]),
        ),
        "session_timeout": dict(
            type="float",
            required=False,
            fallback=(env_fallback, ["VMWARE_SESSION_TIMEOUT"]),
        ),
    }

    argument_spec["allow_guest_control"] = {"type": "bool"}
    argument_spec["backing"] = {"type": "dict"}
    argument_spec["cdrom"] = {"type": "str"}
    argument_spec["ide"] = {"type": "dict"}
    argument_spec["label"] = {"type": "str"}
    argument_spec["sata"] = {"type": "dict"}
    argument_spec["start_connected"] = {"type": "bool"}
    argument_spec["state"] = {
        "type": "str",
        "choices": ["absent", "connect", "disconnect", "present"],
        "default": "present",
    }
    argument_spec["type"] = {"type": "str", "choices": ["IDE", "SATA"]}
    argument_spec["vm"] = {"required": True, "type": "str"}

    return argument_spec


async def main():
    required_if = list([])

    module_args = prepare_argument_spec()
    module = AnsibleModule(
        argument_spec=module_args, required_if=required_if, supports_check_mode=True
    )
    if not module.params["vcenter_hostname"]:
        module.fail_json("vcenter_hostname cannot be empty")
    if not module.params["vcenter_username"]:
        module.fail_json("vcenter_username cannot be empty")
    if not module.params["vcenter_password"]:
        module.fail_json("vcenter_password cannot be empty")
    try:
        session = await open_session(
            vcenter_hostname=module.params["vcenter_hostname"],
            vcenter_username=module.params["vcenter_username"],
            vcenter_password=module.params["vcenter_password"],
            validate_certs=module.params["vcenter_validate_certs"],
            log_file=module.params["vcenter_rest_log_file"],
        )
    except EmbeddedModuleFailure as err:
        module.fail_json(err.get_message())
    result = await entry_point(module, session)
    module.exit_json(**result)


# template: default_module.j2
def build_url(params):
    return ("https://{vcenter_hostname}" "/api/vcenter/vm/{vm}/hardware/cdrom").format(
        **params
    )


async def entry_point(module, session):

    if module.params["state"] == "present":
        if "_create" in globals():
            operation = "create"
        else:
            operation = "update"
    elif module.params["state"] == "absent":
        operation = "delete"
    else:
        operation = module.params["state"]

    func = globals()["_" + operation]

    return await func(module.params, session)


async def _connect(params, session):
    _in_query_parameters = PAYLOAD_FORMAT["connect"]["query"].keys()
    payload = prepare_payload(params, PAYLOAD_FORMAT["connect"])
    subdevice_type = get_subdevice_type(
        "/api/vcenter/vm/{vm}/hardware/cdrom/{cdrom}?action=connect"
    )
    if subdevice_type and not params[subdevice_type]:
        _json = await exists(params, session, build_url(params))
        if _json:
            params[subdevice_type] = _json["id"]
    _url = (
        "https://{vcenter_hostname}"
        # aa
        "/api/vcenter/vm/{vm}/hardware/cdrom/{cdrom}?action=connect"
    ).format(**params) + gen_args(params, _in_query_parameters)
    async with session.post(_url, json=payload, **session_timeout(params)) as resp:
        try:
            if resp.headers["Content-Type"] == "application/json":
                _json = await resp.json()
        except KeyError:
            _json = {}
        if "value" not in _json:  # 7.0.2
            _json = {"value": _json}

        return await update_changed_flag(_json, resp.status, "connect")


async def _create(params, session):

    unicity_keys = ["cdrom"]

    if params["cdrom"]:
        _json = await get_device_info(session, build_url(params), params["cdrom"])
    else:
        _json = await exists(params, session, build_url(params), unicity_keys)
    if _json:
        if "value" not in _json:  # 7.0.2+
            _json = {"value": _json}
        if "_update" in globals():
            params["cdrom"] = _json["id"]
            return await globals()["_update"](params, session)
        return await update_changed_flag(_json, 200, "get")

    payload = prepare_payload(params, PAYLOAD_FORMAT["create"])
    _url = ("https://{vcenter_hostname}" "/api/vcenter/vm/{vm}/hardware/cdrom").format(
        **params
    )
    async with session.post(_url, json=payload, **session_timeout(params)) as resp:
        if resp.status == 500:
            text = await resp.text()
            raise EmbeddedModuleFailure(
                f"Request has failed: status={resp.status}, {text}"
            )
        try:
            if resp.headers["Content-Type"] == "application/json":
                _json = await resp.json()
        except KeyError:
            _json = {}

        if (resp.status in [200, 201]) and "error" not in _json:
            if isinstance(_json, str):  # 7.0.2 and greater
                _id = _json  # TODO: fetch the object
            elif isinstance(_json, dict) and "value" not in _json:
                _id = list(_json["value"].values())[0]
            elif isinstance(_json, dict) and "value" in _json:
                _id = _json["value"]
            _json_device_info = await get_device_info(session, _url, _id)
            if _json_device_info:
                _json = _json_device_info

        return await update_changed_flag(_json, resp.status, "create")


async def _delete(params, session):
    _in_query_parameters = PAYLOAD_FORMAT["delete"]["query"].keys()
    payload = prepare_payload(params, PAYLOAD_FORMAT["delete"])
    subdevice_type = get_subdevice_type("/api/vcenter/vm/{vm}/hardware/cdrom/{cdrom}")
    if subdevice_type and not params[subdevice_type]:
        _json = await exists(params, session, build_url(params))
        if _json:
            params[subdevice_type] = _json["id"]
    _url = (
        "https://{vcenter_hostname}" "/api/vcenter/vm/{vm}/hardware/cdrom/{cdrom}"
    ).format(**params) + gen_args(params, _in_query_parameters)
    async with session.delete(_url, json=payload, **session_timeout(params)) as resp:
        try:
            if resp.headers["Content-Type"] == "application/json":
                _json = await resp.json()
        except KeyError:
            _json = {}
        return await update_changed_flag(_json, resp.status, "delete")


async def _disconnect(params, session):
    _in_query_parameters = PAYLOAD_FORMAT["disconnect"]["query"].keys()
    payload = prepare_payload(params, PAYLOAD_FORMAT["disconnect"])
    subdevice_type = get_subdevice_type(
        "/api/vcenter/vm/{vm}/hardware/cdrom/{cdrom}?action=disconnect"
    )
    if subdevice_type and not params[subdevice_type]:
        _json = await exists(params, session, build_url(params))
        if _json:
            params[subdevice_type] = _json["id"]
    _url = (
        "https://{vcenter_hostname}"
        # aa
        "/api/vcenter/vm/{vm}/hardware/cdrom/{cdrom}?action=disconnect"
    ).format(**params) + gen_args(params, _in_query_parameters)
    async with session.post(_url, json=payload, **session_timeout(params)) as resp:
        try:
            if resp.headers["Content-Type"] == "application/json":
                _json = await resp.json()
        except KeyError:
            _json = {}
        if "value" not in _json:  # 7.0.2
            _json = {"value": _json}

        return await update_changed_flag(_json, resp.status, "disconnect")


async def _update(params, session):
    payload = prepare_payload(params, PAYLOAD_FORMAT["update"])
    _url = (
        "https://{vcenter_hostname}" "/api/vcenter/vm/{vm}/hardware/cdrom/{cdrom}"
    ).format(**params)
    async with session.get(_url, **session_timeout(params)) as resp:
        _json = await resp.json()
        if "value" in _json:
            value = _json["value"]
        else:  # 7.0.2 and greater
            value = _json
        for k, v in value.items():
            if k in payload:
                if isinstance(payload[k], dict) and isinstance(v, dict):
                    to_delete = True
                    for _k in list(payload[k].keys()):
                        if payload[k][_k] != v.get(_k):
                            to_delete = False
                    if to_delete:
                        del payload[k]
                elif payload[k] == v:
                    del payload[k]
                elif payload[k] == {}:
                    del payload[k]

        if payload == {} or payload == {"spec": {}}:
            # Nothing has changed
            if "value" not in _json:  # 7.0.2
                _json = {"value": _json}
            _json["id"] = params.get("cdrom")
            return await update_changed_flag(_json, resp.status, "get")
    async with session.patch(_url, json=payload, **session_timeout(params)) as resp:
        try:
            if resp.headers["Content-Type"] == "application/json":
                _json = await resp.json()
        except KeyError:
            _json = {}
        if "value" not in _json:  # 7.0.2
            _json = {"value": _json}

        # e.g: content_configuration
        if not _json and resp.status == 204:
            async with session.get(_url, **session_timeout(params)) as resp_get:
                _json_get = await resp_get.json()
                if _json_get:
                    _json = _json_get

        _json["id"] = params.get("cdrom")
        return await update_changed_flag(_json, resp.status, "update")


if __name__ == "__main__":
    import asyncio

    current_loop = asyncio.get_event_loop_policy().get_event_loop()
    current_loop.run_until_complete(main())
