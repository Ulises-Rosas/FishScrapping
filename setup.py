#!/usr/bin/env python3

import setuptools
from distutils.core import setup

setup(name="FishScrapping",
      version='1.0',
      author='Ulises Rosas',
      author_email='ulisesfrosasp@gmail.com',
      url='https://github.com/Ulises-Rosas/OBISdat',
      packages = ['FishScrapping'],
      package_dir = {'FishScrapping': 'src'},
      scripts = ['src/fishbase.py']
      )

