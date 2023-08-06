#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: ZHANG XINZENG
# Created on 2020-05-03 19:31

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="google-translate-for-goldendict-academic",
    version="0.0.12",
    author="zli",
    author_email="1036281414@qq.com",
    description="Modified from google-translate-for-goldendict (xinebf)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/xinebf/google-translate-for-goldendict",
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
