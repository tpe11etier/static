#!/usr/bin/env python

from distutils.core import setup

setup(name='static',
      version='0.1',
      description='Static Prompt Uploader',
      author='Tony Pelletier',
      author_email='tony.pelletier@gmail.com',
      py_modules = ['static', 'MultipartPostHandler', 'BeautifulSoup']
     )
