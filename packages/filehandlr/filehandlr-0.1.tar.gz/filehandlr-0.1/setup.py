import re

import setuptools

version = 0.1
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

name = "filehandlr"
author = "Spidy"
author_email = "sppidytg@gmail.com"
description = "This Package Contains Fuctions Which can handle Files. For Now It can handle only simple text files."
license = "GNU AFFERO GENERAL PUBLIC LICENSE (v3)"
url = "https://github.com/sppidy/filehandlr"
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
]
requirements = []


setuptools.setup(
    name=name,
    version=version,
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    license=license,
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=classifiers,
    python_requires=">=3.6",
)
