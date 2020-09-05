import os
from setuptools import setup, find_packages
from pip._internal.req import parse_requirements

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def load_requirements(fname):
    reqs = parse_requirements(fname, session="test")
    return [str(ir.req) for ir in reqs]


setup(
    name="torrent_searcher",
    version="1.0.0",
    author="Federico Rulli",
    author_email="fede.rulli@gmail.com",
    description="Torrent Searcher",
    install_requires=load_requirements("requirements.txt"),
    packages=find_packages(),
    long_description=read('README.md')
)
