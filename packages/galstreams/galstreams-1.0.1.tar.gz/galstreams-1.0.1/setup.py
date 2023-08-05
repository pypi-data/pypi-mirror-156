import os
import sys
import re

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

long_description = ""
with open('README.md', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='galstreams',
    version='1.0.1',
    author='C. Mateu',
    author_email='cmateu@fisica.edu.uy',
    packages=['galstreams','galstreams/lib','galstreams/tracks'],
    package_data={'galstreams/lib':['*.dat',
                                   '*.log',
                                   'master*',
                                   'streams_lib_notes.ipynb',
                                   'globular_cluster_params.harris2010.tableI.csv'],
		  'galstreams/tracks':['*.ecsv'],
		  'galstreams/notebooks':['*ipy*']},
#    scripts=['bin/'],
    url='https://github.com/cmateu/galstreams',
    license='BSD-3-Clause',
    description='MW stream library toolkit',
    long_description=long_description,
    install_requires=[
      "numpy",
      "scipy",
      "astropy",
    ],
    python_requires='>=3.5',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.5",
        "Topic :: Scientific/Engineering :: Astronomy"
    ],
)
