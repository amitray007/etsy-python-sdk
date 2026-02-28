from setuptools import setup, find_packages
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

# Read version from _version.py
def read_version():
    version_file = os.path.join(here, "etsy_python", "_version.py")
    with open(version_file, "r") as f:
        version_content = f.read()
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', version_content)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = read_version()
DESCRIPTION = "Etsy API Client Library for Python"

# Setting up
setup(
    name="etsy-python",
    version=VERSION,
    author="Amit Ray",
    author_email="mail@amitray.dev",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=["requests", "requests-oauthlib"],
    keywords=["python", "etsy", "api"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    project_urls={
        "Documentation": "https://github.com/amitray007/etsy-python-sdk/blob/master/README.md",
        "Source code": "https://github.com/amitray007/etsy-python-sdk",
        "Issues": "https://github.com/amitray007/etsy-python-sdk/issues",
    },
)
