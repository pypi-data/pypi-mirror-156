# -*- coding: utf-8 -*-
"""
basic helper stuff for safely handling shell commands
"""

import shlex
from collections import UserList


class ShellCommand(UserList):
    """
    wrapper class for list of shell-quoted command-line arguments
    """

    def __init__(self, cmd_exec, args):
        UserList.__init__(self, [cmd_exec] + args)

    def __str__(self):
        return ' '.join(shlex.quote(arg) for arg in self)
