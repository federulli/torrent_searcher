import os
from setuptools import setup, find_packages

path = os.path.dirname(os.path.realpath(__file__))
requirement_path = f'{path}/requirements.txt'

install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="torrent_searcher",
    version="1.0.0",
    author="Federico Rulli",
    author_email="fede.rulli@gmail.com",
    description="Torrent Searcher",
    install_requires=install_requires,
    packages=find_packages(),
    long_description=read('README.md')
)
