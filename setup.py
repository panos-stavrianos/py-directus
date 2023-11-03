#!/usr/bin/env python

import pathlib

from setuptools import setup, find_packages

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()

readme = pathlib.Path('README.md').read_text()

setup(
    author="Panos Stavrianos",
    author_email='panos@orbitsystems.gr',
    python_requires='>=3.6',
    description="Python wrapper for asynchronous interaction with Directus",
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords=['svelte', 'web components', 'python', 'fastapi', 'flask'],
    name='py_directus',
    packages=find_packages(include=['py_directus', 'py_directus.*']),
    url='https://github.com/panos-stavrianos/py-directus',
    version='{{VERSION_PLACEHOLDER}}',
    zip_safe=False
)
