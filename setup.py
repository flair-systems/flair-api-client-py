#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='flair-client',
      version='1.1.0',
      description='Flair API Client',
      author='Edward Paget',
      author_email='ed@flair.co',
      maintainer='Derrick A.',
      maintainer_email='derrick@flair.co',
      url='https://api.flair.co',
      packages=find_packages(),
      python_requires='>=3.5',
      install_requires=['requests']
)