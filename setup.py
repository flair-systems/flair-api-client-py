#!/usr/bin/env python

from setuptools import setup

setup(name='flair-client',
      version='0.0.1',
      description='Flair API Client',
      author='Edward Paget',
      author_email='ed@flair.co',
      url='https://api.flair.co',
      packages=['flair_api'],
      install_requires=['requests']
)
