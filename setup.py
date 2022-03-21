# -*- encoding: utf-8 -*-
"""
A setuptools-based setup module.
See:
   https://packaging.python.org/en/latest/distributing.html
Docs on the setup function kwargs:
   https://packaging.python.org/distributing/#setup-args
"""

from __future__ import absolute_import, print_function
import os
import os.path
from setuptools import setup, find_packages
import re

# Get the version data from the main __init__.py file.
with open(os.path.join("applib_async", "__init__.py")) as f:
    __version__ = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read()).group(1)

# To package external data, which includes an executable, the package_dir
# option tends to be better than the data_files option, which does not preserve
# the directory structure and puts the data in the wrong place for package data
# upon installation.  To use package_data all directory names must be valid
# package names, though, and you also need an __init__.py in each such
# directory and subdirectory.

package_dir = {"": "."}
packages = find_packages(".", exclude=["tests"]) # Finds submodules (otherwise need explicit listing).

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()
install_requires += ["wheel",
                    "python_version>='3.8.0'"]


setup(
    name="applib-async",
    version=__version__, # <majorVersion>.<minorVersion>.<patch> format, (see PEP440)
    description="A set of cross-platform application utilities",
    keywords=["applib", "utilities", "async", "asyncio"],
    python_requires=">=3.8",
    install_requires=install_requires,
    url="https://github.com/killbus/python-applib-async",
    license="GPL",
    classifiers=[
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        # Development Status: Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        # uncomment if you test on these interpreters:
        # "Programming Language :: Python :: Implementation :: IronPython",
        # "Programming Language :: Python :: Implementation :: Jython",
        # "Programming Language :: Python :: Implementation :: Stackless",
        "Topic :: Utilities",
    ],

    # Settings usually the same.
    author="killbus",
    author_email="killbus@users.noreply.github.com",

    #include_package_data=True, # Not set True when package_data is set.
    zip_safe=False,

    # Automated stuff below
    packages=packages,
    package_dir=package_dir
)
