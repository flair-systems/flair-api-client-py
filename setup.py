#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='flair-client',
      version='2.0.0',
      description='Flair API Client',
      author='Edward Paget',
      author_email='ed@flair.co',
      url='https://api.flair.co',
      packages=find_packages(),
      python_requires='>=3.8',
      install_requires=['requests'],
      extras_require={
          'dev': ['python-dotenv>=1.0.0,<2.0.0']
      }
)