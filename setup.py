#!/usr/bin/env python
""" Python simple CLI to interact with Nokia Napalm driver. """

from setuptools import setup, find_packages

version = '0.0.4'
setup(
    name='pysros',
    version=version,
    py_modules=['pysros'],
    packages=find_packages(),
    install_requires=[
        "napalm==3.3.1",
        # git+https://git@github.com/napalm-automation-community/
        "napalm-sros",
        "PyYAML"
    ],
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
    python_requires='~=3.0',
    entry_points={
        'console_scripts': ['pysros=pysros.command_line:main'],
    }
)
