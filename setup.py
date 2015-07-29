# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="moneywagon",
    version='1.2.2',
    description='Toolset for getting the exchange rate for cryptocurrencies',
    long_description=open('README.md').read(),
    author='Chris Priest',
    author_email='cp368202@ohiou.edu',
    url='https://github.com/priestc/moneywagon',
    packages=find_packages(),
    scripts=['bin/moneywagon'], # coming soon
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
        'pytz',
        'arrow',
        'pybitcointools'
    ]
)
