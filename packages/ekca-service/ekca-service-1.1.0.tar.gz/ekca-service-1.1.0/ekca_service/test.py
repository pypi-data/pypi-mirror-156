# -*- coding: utf-8 -*-
"""
stuff for testing
"""

import unittest

# from setuptools
import pkg_resources

from ekca_service.__about__ import PASSWORD_PLUGIN_NAMESPACE, OTP_PLUGIN_NAMESPACE


class PasswordPluginTestCase(unittest.TestCase):
    """
    base unit test class (not directly used)
    """

    plugin_name = None

    def setUp(self):
        self.password_plugins = {
            entry_point.name: entry_point.load()
            for entry_point
            in pkg_resources.iter_entry_points(PASSWORD_PLUGIN_NAMESPACE)
        }


class OTPPluginTestCase(unittest.TestCase):
    """
    base unit test class (not directly used)
    """

    plugin_name = None

    def setUp(self):
        self.otp_plugins = {
            entry_point.name: entry_point.load()
            for entry_point in pkg_resources.iter_entry_points(OTP_PLUGIN_NAMESPACE)
        }
