# -*- coding: utf-8 -*-
"""
ekca_service.plugins.otp - Module package for separate OTP checker plugins
"""

import ssl
from urllib.parse import urlparse

__all__ = [
    'OTPChecker',
    'OTPWebService',
]


class OTPCheckFailed(Exception):
    """
    base exception class for all OTP failures
    """


class OTPChecker:
    """
    Base class for OTP checker plugin classes, not directly used!
    """

    def __init__(self, cfg, logger):
        """
        :cfg: is config dict
        """
        self._log = logger
        self._cfg = cfg

    def check(self, username, otp):
        """
        actually check whether OTP is valid for username
        """
        raise OTPCheckFailed('%s.check() must not be used directly!' % (self.__class__.__name__,))


class Dummy(OTPChecker):
    """
    Dummy OTP checker always returning True for pre-defined set of OTP values
    """
    cfg_key_values = 'OTP_DUMMY_VALUES'
    values_default = '123456 12345678 abcd1234567890123456'

    def __init__(self, cfg, logger):
        OTPChecker.__init__(self, cfg, logger)
        self._valid_otp_values = frozenset([
            val
            for val in self._cfg.get(
                self.cfg_key_values,
                self.values_default
            ).replace(',', ' ').split(' ')
            if val
        ])

    def check(self, username, otp):
        if otp not in self._valid_otp_values:
            raise OTPCheckFailed()


class OTPWebService(OTPChecker):
    """
    Base class for OTP checker plugin classes which
    send requests to web services

    Not directly used!
    """
    req_mime_type = 'application/json'
    cfg_key_url = 'OTP_CHECK_URL'
    cfg_key_cacerts = 'OTP_CHECK_CACERTS'
    cacerts_default = '/etc/ssl/ca-bundle.pem'

    def __init__(self, cfg, logger):
        """
        Additionally parse URL read from config vars and set
        CA cert file read from config or default
        """
        OTPChecker.__init__(self, cfg, logger)
        self._url = urlparse(self._cfg[self.cfg_key_url])
        self._ca_certs = self._cfg.get(self.cfg_key_cacerts, self.cacerts_default)

    def _ssl_context(self):
        ctx = ssl.SSLContext()
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.check_hostname = True
        ctx.load_verify_locations(cafile=self._ca_certs, capath=None, cadata=None)
        return ctx
