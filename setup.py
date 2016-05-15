# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import sys

if sys.version_info <= (3,1):
    extra_install = ['futures']
else:
    extra_install = []

setup(
    name="moneywagon",
    version='1.10.9',
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
        'bitcoin'
    ] + extra_install
)
