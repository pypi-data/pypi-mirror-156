#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glob import glob
from setuptools import setup, Extension
import os, sys, re


with open('README.md', 'r') as fd:
  version = '0.8'
  author = 'Ryou Ohsawa'
  email = 'ohsawa@ioa.s.u-tokyo.ac.jp'
  description = 'MinimalKNN: minimal package to construct k-NN Graph'
  long_description = fd.read()
  license = 'MIT'


with open('requirements.txt', 'r') as fd:
  requirements = []
  for l in fd.readlines(): requirements.append(l.rstrip())


classifiers = [
  'Development Status :: 3 - Alpha',
  'Environment :: Console',
  'Intended Audience :: Science/Research',
  'License :: OSI Approved :: MIT License',
  'Operating System :: POSIX :: Linux',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python :: 3.7',
  'Programming Language :: Python :: Implementation :: CPython',
  'Topic :: Scientific/Engineering :: Astronomy']


if __name__ == '__main__':
  from Cython.Distutils import build_ext
  from Cython.Build import cythonize
  import numpy

  extensions   = [
    Extension(
      'minimalKNN',
      language           = 'c++',
      sources            = ['minimalKNN.pyx'] + glob(os.path.join('src', '*.cc')),
      libraries          = ['m',],
      include_dirs       = [numpy.get_include(), 'src'],
      depends            = glob(os.path.join('src', '*.h')),
      extra_compile_args = ['-std=c++11','-O2'],
    )
  ]

  extensions = cythonize(extensions, language_level=3)
  cmdclass = {'build_ext': build_ext}

  setup(
    name='minimalKNN',
    version=version,
    author=author,
    author_email=email,
    maintainer=author,
    maintainer_email=email,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/ryou_ohsawa/minimalKNN/src/master/',
    license=license,
    classifiers=classifiers,
    install_requires=requirements,
    cmdclass=cmdclass,
    ext_modules=extensions)
