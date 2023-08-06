#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools
from distutils.core import setup, Extension

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

module1 = Extension('tamodify',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
                    include_dirs = ['../c'],
#                    libraries = [''],
#                    library_dirs = ['/usr/local/lib'],
                    sources = ['src/tamodify.c','../c/tajk_data.c','../c/tajk_modify.c'])

setuptools.setup(
    name="tamodify",
    version="0.0.1",
    author="Chen chuan",
    author_email="13902950907@139.com",
    description="TA接口文件修改",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    zip_safe= False,
    include_package_data = True,
    ext_modules = [module1],
)
