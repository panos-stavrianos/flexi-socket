#!/usr/bin/env python

import os
from pathlib import Path

from setuptools import setup, find_packages

requirements = []
if os.path.exists('requirements.txt'):
    with open('requirements.txt') as requirements_file:
        requirements = requirements_file.readlines()

readme = Path('README.md').read_text()
version = '{{VERSION_PLACEHOLDER}}'
if "VERSION_PLACEHOLDER" in version:
    version = '0.0.1'
setup(
    author="Panos Stavrianos",
    author_email='panos@orbitsystems.gr',
    python_requires='>=3.6',
    description="Socket wrapper for asyncio",
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords=['flexi_socket', 'socket', 'asyncio', 'async', 'tcp', 'udp', 'socket wrapper'],
    name='py_directus',
    packages=find_packages(include=['flexi_socket', 'flexi_socket.*']),
    url='https://github.com/panos-stavrianos/flexi-socket',
    version=version,
    zip_safe=False
)
