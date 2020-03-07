#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


with open('README.md', 'r') as fp:
    README = fp.read()


setup(
    name='fingerprint',
    version='0.1.4',
    description='Document fingerprint generator',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Kailash Budhathoki',
    author_email='kailash.buki@gmail.com',
    url='http://github.com/kailashbuki/fingerprint',
    license='MIT License',
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
