#!/usr/bin/env python
""" Python library to remotely manage/automate
 switches running OcNOS operating system. """

from setuptools import setup, find_packages

with open('requirements.txt', 'r') as requirements:
    install_requires = [line.strip() for line in requirements if line and not line.startswith('#')]

version = '0.0.1'
setup(
    name='pysros',
    version=version,
    py_modules=['pysros'],
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    description='Python simple CLI to interact with Nokia Napalm Driver',
    author='LINX',
    author_email='developers@linx.net',
    url='https://github.com/LINXNet/pysros/',
    download_url='https://github.com/LINXNet/pysros/tarball/%s' % version,
    keywords=['SROS', 'networking'],
    classifiers=[
         'Programming Language :: Python :: 3'
     ],
    python_requires='~=3.6.6',
    entry_points={
        'console_scripts': ['pysros=pysros.command_line:main'],
    }
)