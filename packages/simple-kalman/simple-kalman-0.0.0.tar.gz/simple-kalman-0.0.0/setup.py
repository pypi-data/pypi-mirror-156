#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 20:51:46 2022

@author: eadali
"""

from distutils.core import setup
setup(
  name = 'simple-kalman',
  #packages = ['advanced_pid', 'advanced_pid.integrate', 'advanced_pid.models'],
  version = '0.0.0',
  license='MIT',
  description = 'kalman',
  long_description='kalman',
  author = 'Erkan ADALI',
  author_email = 'erkanadali91@gmail.com',
  url = 'https://github.com/eadali/simple-kalman',
  project_urls={'Documentation': 'https://simple-kalman.readthedocs.io/',
                'Source Code': 'https://github.com/eadali/simple-kalman',},
  keywords = ['control', 'theory', 'engineering', 'kalman', 'real', 'time',],
  install_requires=['numpy',],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],
)