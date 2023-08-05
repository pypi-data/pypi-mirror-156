#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:  smeggingsmegger
# Purpose: setup
# Created: 2016-06-23
#
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='PyWebRunner',
    version='2.6.0',
    url='http://github.com/smeggingsmegger/PyWebRunner',
    license='MIT',
    author='Scott Blevins',
    author_email='scott@factobot.com',
    description='A library that extends and improves the Selenium python library.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms='OS Independent',
    packages=['PyWebRunner'],
    data_files=[('extensions', ['JSErrorCollector.xpi', 'JSErrorCollector.crx'])],
    include_package_data=True,
    install_requires=['xvfbwrapper', 'selenium', 'pyaml'],
    keywords=['Selenium', 'Testing'],
    entry_points='''
        [console_scripts]
        webrunner=PyWebRunner.runner:main
    ''',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: User Interfaces",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
