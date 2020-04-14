from setuptools import setup

import nap

NAME = 'python-nap'
VERSION = nap.VERSION
DESCRIPTION = "Python Monitoring Plugins Library"
LONG_DESCRIPTION = """
Library to help write monitoring plugins in python
"""
AUTHOR = nap.AUTHOR
AUTHOR_EMAIL = nap.AUTHOR_EMAIL
LICENSE = "ASL 2.0"
PLATFORMS = "Any"
URL = "https://gitlab.cern.ch/etf/nap"
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Software Development :: Libraries :: Python Modules"
]

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      platforms=PLATFORMS,
      url=URL,
      classifiers=CLASSIFIERS,
      keywords='operations python Nagios Monitoring plugins',
      packages=['nap'],
      install_requires=['argparse'],
      )
