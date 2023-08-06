#This is setup.py file to set all details of the package here

from setuptools import setup

__project__ = "ep2"
__version__ = "22.1.2"
__description__ = "This is test package to learn distribution on open source"
__packages__ = ["printName"]
__author__ = "EP"


setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    author = __author__,
    )
