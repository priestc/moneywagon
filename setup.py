# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import sys

extra_install = []
if sys.version_info <= (3,1):
    extra_install.append('futures')

if sys.version_info <= (3,6):
    extra_install.append('pysha3')

setup(
    name="moneywagon",
    version='1.16.12',
    description='Next Generation Cryptocurrency Platform',
    long_description=open('README.md').read(),
    author='Chris Priest',
    author_email='cp368202@ohiou.edu',
    url='https://github.com/priestc/moneywagon',
    packages=find_packages(),
    scripts=['bin/moneywagon'],
    include_package_data=True,
    license='LICENSE',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'requests',
        'tabulate',
        'base58',
        'pytz',
        'arrow',
        'bitcoin',
        'beautifulsoup4'
    ] + extra_install
)
