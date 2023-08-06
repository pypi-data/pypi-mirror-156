#!/usr/bin/env python3
from setuptools import setup, find_packages

import os

__requires = [dep.split('#')[0].strip() for dep in filter(None, open('requirements.txt').read().splitlines())] 

setup(
    name='ajenti.plugin.fstab',
    version='0.4',
    python_requires='>=3',
    install_requires=__requires,
    description='Fstab',
    long_description='A Fstab plugin for Ajenti panel',
    author='Arnaud Kientz',
    author_email='arnaud@linuxmuster.net',
    url='https://ajenti.org',
    packages=find_packages(),
    include_package_data=True,
)