# -*- coding: utf-8 -*-
"""
ekca_service.plugins.password - Module package for password checker plugins
"""

__all__ = [
    'PasswordChecker',
]

from collections import defaultdict


class PasswordCheckFailed(Exception):
    """
    base exception class for all password failures
    """


class PasswordChecker:
    """
    Base class for password checker plugin classes, not directly used!
    """

    def __init__(self, cfg, logger):
        """
        :cfg: is config dict
        """
        self._log = logger
        self._cfg = cfg

    def check(self, user_name, password, remote_addr):
        """
        actually check whether password is valid for username
        """
        raise PasswordCheckFailed()


class Dummy(PasswordChecker):
    """
    Dummy OTP checker always returning True for pre-defined set of OTP values
    """
    cfg_key_values = 'PASSWORD_DUMMY_VALUES'
    values_default = 'secret123456 12345678 supersecret'

    def __init__(self, cfg, logger):
        PasswordChecker.__init__(self, cfg, logger)
        self._valid_passwords = frozenset([
            val
            for val in self._cfg.get(
                self.cfg_key_values,
                self.values_default
            ).replace(',', ' ').split(' ')
            if val
        ])

    def check(self, user_name, password, remote_addr):
        if password not in self._valid_passwords:
            raise PasswordCheckFailed()
        return dict(attributes=defaultdict(lambda: []))
