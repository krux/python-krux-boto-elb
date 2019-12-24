# -*- coding: utf-8 -*-
#
# © 2019 Salesforce.com
#

"""
Package setup for krux-elb
"""

#
# Standard libraries
#
from setuptools import setup, find_packages

from krux_elb import __version__

# URL to the repository on Github.
REPO_URL = 'https://github.com/krux/python-krux-boto-elb'
# Github will generate a tarball as long as you tag your releases, so don't
# forget to tag!
DOWNLOAD_URL = ''.join((REPO_URL, '/tarball/release/', __version__))


setup(
    name='krux-elb',
    version=__version__,
    author='Peter Han',
    maintainer='David Llopis',
    maintainer_email='dllopis@salesforce.com',
    description='Library for interacting with AWS ELB built on krux-boto',
    url=REPO_URL,
    download_url=DOWNLOAD_URL,
    license='All Rights Reserved.',
    packages=find_packages(),
    install_requires=[
        'krux-boto',
    ],
)
