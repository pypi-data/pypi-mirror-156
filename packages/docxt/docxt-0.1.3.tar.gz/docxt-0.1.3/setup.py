#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

setup(
    name='docxt',
    version='0.1.3',
    author='barwe',
    author_email='barwechin@163.com',
    url='https://pypi.org/project/docxt',
    description='A simple way to generate a report from a template.',
    packages=['docxt', 'docxt.utils'],
    install_requires=['docxtpl', 'beautifulsoup4'],
)
