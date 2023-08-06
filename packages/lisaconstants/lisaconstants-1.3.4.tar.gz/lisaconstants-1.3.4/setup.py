#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Dict
import setuptools
from setuptools.command.install import install

from lisaconstants.constants import Constant
from lisaconstants.cheader import HeaderGenerator


class InstallHeaders(install):
    """Automatically generate C/C++ headers and install them."""

    def run(self):
        super().run()

        self.mkpath(self.install_headers)
        generator = HeaderGenerator(Constant.ALL)

        out = os.path.join(self.install_headers, 'lisaconstants.hpp')
        generator.write(out, 'c++')

        out = os.path.join(self.install_headers, 'lisaconstants.h')
        generator.write(out, 'c')


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

meta: Dict[str, str] = {}
with open('lisaconstants/meta.py', encoding='utf-8') as file:
    exec(file.read(), meta)


setuptools.setup(
    name="lisaconstants",
    version=meta['__version__'],
    author=meta['__author__'],
    author_email=meta['__email__'],
    description="LISA Python Constants provides values sanctioned by the LISA Consortium for physical constants and mission parameters.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.in2p3.fr/lisa-simulation/constants",
    packages=setuptools.find_packages(),
    install_requires=[],
    tests_require=['pytest'],
    python_requires='>=3.7',
    cmdclass={'install': InstallHeaders}
)
