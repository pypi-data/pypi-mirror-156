# -*- coding: utf-8 -*-
"""
package/install module package ekca-service
"""

import sys
import os
from setuptools import setup

PYPI_NAME = 'ekca-plugin-aedir'

BASEDIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, os.path.join(BASEDIR, 'ekca_service', 'plugins', 'password', 'aedir'))
import __about__

setup(
    name=PYPI_NAME,
    license=__about__.__license__,
    version=__about__.__version__,
    description='EKCA service password plugin for Æ-DIR',
    author=__about__.__author__,
    author_email=__about__.__mail__,
    maintainer=__about__.__author__,
    maintainer_email=__about__.__mail__,
    url='https://ekca.stroeder.com',
    download_url='https://pypi.python.org/pypi/'+PYPI_NAME,
    keywords=['Æ-DIR', 'AE-DIR', 'PKI', 'SSH', 'SSH-CA', 'Certificate'],
    packages=['ekca_service.plugins.password.aedir'],
    package_dir={'': '.'},
    test_suite='tests',
    python_requires='>=3.6.*',
    include_package_data=True,
    data_files=[],
    install_requires=[
        'setuptools',
        'ekca-service>={version}'.format(version=__about__.__version__),
        'aedir>=1.4',
    ],
    zip_safe=False,
    entry_points={
        'ekca_service.plugins.password': [
            'aedir = ekca_service.plugins.password.aedir:AEDirPasswordChecker',
        ],
    },
)
