from setuptools import setup, find_packages

setup(
    name=‘pycryptoprices’,
    version='1.0',
    description='',
    long_description=open('README.md’).read(),
    author='Chris Priest',
    author_email='cp368202@ohiou.edu',
    url='https://github.com/priestc/pycryptoprices',
    packages=find_packages(),
    scripts=['bin/cryptopricecmd’],
    include_package_data=True,
    license='LICENSE',  
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        'requests'
    ]
)