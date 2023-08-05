#!/usr/bin/env python

import os.path as op

from setuptools import setup

version = '1.0.0'
basedir = op.dirname(__file__)

with open(op.join(basedir, 'README.rst'), 'rt') as f:
    readme = f.read()

setup(
    name='fmrib-unpack-fmrib-config',
    version=version,
    description='The FUNPACK FMRIB configuration profile',
    long_description=readme,
    url='https://git.fmrib.ox.ac.uk/fsl/funpack-fmrib-config',
    author='Paul McCarthy',
    author_email='pauldmccarthy@gmail.com',
    license='Apache License Version 2.0',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    include_package_data=True,
    packages=['funpack', 'funpack.plugins'],
)
