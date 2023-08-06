#!/usr/bin/env python

from distutils.core import setup

long_desc = 'Licensed under the generic MIT License.\"farewell-cache\" can be ' \
            'installed via \"pip\".'
version = ''

with open("version.txt", "r", encoding="utf-8") as fh:
    version = fh.read()
    fh.close()

setup(name='farewell-cache',
      version=version,
      py_modules=['farewell-cache'],
      description='Farewell Cache | The Cache Deleter',
      long_description=long_desc,
      long_description_content_type='text/markdown',
      author='Tushar Iyer',
      author_email='',
      url='https://github.com/tushariyer/farewell-cache',
      project_urls={
              "Bug Tracker": "https://github.com/tushariyer/farewell-cache/issues",
          }
      )