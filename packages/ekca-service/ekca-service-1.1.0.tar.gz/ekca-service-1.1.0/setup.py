# -*- coding: utf-8 -*-
"""
package/install module package ekca-service
"""

import sys
import os
from setuptools import setup, find_packages

PYPI_NAME = 'ekca-service'

BASEDIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, os.path.join(BASEDIR, 'ekca_service'))
import __about__


def name_spaces():
    name_spaces = set()
    for name_space in (__about__.OTP_PLUGIN_NAMESPACE, __about__.PASSWORD_PLUGIN_NAMESPACE):
        name_lst = name_space.split('.')
        name_spaces.update(['.'.join(name_lst[:i+1]) for i in range(len(name_lst))])
    return sorted(name_spaces)


setup(
    name=PYPI_NAME,
    license=__about__.__license__,
    version=__about__.__version__,
    description='EKCA service',
    author=__about__.__author__,
    author_email=__about__.__mail__,
    maintainer=__about__.__author__,
    maintainer_email=__about__.__mail__,
    url='https://ekca.stroeder.com',
    download_url='https://pypi.python.org/pypi/'+PYPI_NAME,
    keywords=['PKI', 'SSH', 'SSH-CA', 'Certificate'],
    packages=find_packages(exclude=['tests']),
    package_dir={'': '.'},
    test_suite='tests',
    python_requires='>=3.6.*',
    include_package_data=True,
    data_files=[],
    install_requires=[
        'setuptools',
        'flask>=0.12',
        'PyNaCl>=1.2',
        'paramiko>=2.4',
    ],
    zip_safe=False,
    namespace_packages=name_spaces(),
    entry_points={
        __about__.OTP_PLUGIN_NAMESPACE: [
            'dummy = {0}.base:Dummy'.format(__about__.OTP_PLUGIN_NAMESPACE)
        ],
        __about__.PASSWORD_PLUGIN_NAMESPACE: [
            'dummy = {0}.base:Dummy'.format(__about__.PASSWORD_PLUGIN_NAMESPACE),
        ],
    },
)
