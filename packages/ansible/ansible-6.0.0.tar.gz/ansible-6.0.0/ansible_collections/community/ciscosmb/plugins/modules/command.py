#!/usr/bin/python

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: command
author: "Petr Klima (@qaxi)"
short_description: Run commands on remote Cisco SMB devices
description:
  - Sends arbitrary commands to an Cisco SMB node and returns the results
    read from the device. This module includes an
    argument that will cause the module to wait for a specific condition
    before returning or timing out if the condition is not met.
options:
  commands:
    description:
      - List of commands to send to the remote Cisco SMB device over the
        configured provider. The resulting output from the command
        is returned. If the I(wait_for) argument is provided, the
        module is not returned until the condition is satisfied or
        the number of retries has expired.
    required: true
    type: list
    elements: str
  wait_for:
    description:
      - List of conditions to evaluate against the output of the
        command. The task will wait for each condition to be true
        before moving forward. If the conditional is not true
        within the configured number of retries, the task fails.
        See examples.
    type: list
    elements: str
  match:
    description:
      - The I(match) argument is used in conjunction with the
        I(wait_for) argument to specify the match policy.  Valid
        values are C(all) or C(any).  If the value is set to C(all)
        then all conditionals in the wait_for must be satisfied.  If
        the value is set to C(any) then only one of the values must be
        satisfied.
    default: all
    type: str
    choices: ['any', 'all']
  retries:
    description:
      - Specifies the number of retries a command should by tried
        before it is considered failed. The command is run on the
        target device every retry and evaluated against the
        I(wait_for) conditions.
    default: 10
    type: int
  interval:
    description:
      - Configures the interval in seconds to wait between retries
        of the command. If the command does not pass the specified
        conditions, the interval indicates how long to wait before
        trying the command again.
    default: 1
    type: int
'''

EXAMPLES = """
- name: Run command on remote devices
  community.ciscosmb.command:
    commands: show version

- name: Run command and check to see if output contains PID
  community.ciscosmb.command:
    commands: show inventory
    wait_for: result[0] contains PID

- name: Run multiple commands on remote nodes
  community.ciscosmb.command:
    commands:
      - show version
      - show system

- name: Run multiple commands and evaluate the output
  community.ciscosmb.command:
    commands:
      - show version
      - show system
    wait_for:
      - result[0] contains Active-image
      - result[1] contains "System Up Time"
"""

RETURN = """
stdout:
  description: The set of responses from the commands.
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: ['...', '...']
stdout_lines:
  description: The value of stdout split into a list.
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: [['...', '...'], ['...'], ['...']]
failed_conditions:
  description: The list of conditionals that have failed.
  returned: failed
  type: list
  sample: ['...', '...']
"""

import time

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.parsing import Conditional
from ansible_collections.community.ciscosmb.plugins.module_utils.ciscosmb import run_commands
from ansible_collections.community.ciscosmb.plugins.module_utils.ciscosmb import ciscosmb_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import string_types


def to_lines(stdout):
    for item in stdout:
        if isinstance(item, string_types):
            item = str(item).split('\n')
        yield item


def main():
    """main entry point for module execution
    """
    argument_spec = dict(
        commands=dict(type='list', elements='str', required=True),

        wait_for=dict(type='list', elements='str'),
        match=dict(default='all', choices=['all', 'any']),

        retries=dict(default=10, type='int'),
        interval=dict(default=1, type='int')
    )

    argument_spec.update(ciscosmb_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)

    result = {'changed': False}

    wait_for = module.params['wait_for'] or list()
    conditionals = [Conditional(c) for c in wait_for]

    retries = module.params['retries']
    interval = module.params['interval']
    match = module.params['match']

    while retries > 0:
        responses = run_commands(module, module.params['commands'])

        for item in list(conditionals):
            if item(responses):
                if match == 'any':
                    conditionals = list()
                    break
                conditionals.remove(item)

        if not conditionals:
            break

        time.sleep(interval)
        retries -= 1

    if conditionals:
        failed_conditions = [item.raw for item in conditionals]
        msg = 'One or more conditional statements have not been satisfied'
        module.fail_json(msg=msg, failed_conditions=failed_conditions)

    result.update({
        'changed': False,
        'stdout': responses,
        'stdout_lines': list(to_lines(responses))
    })

    module.exit_json(**result)


if __name__ == '__main__':
    main()
