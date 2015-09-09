import os
from distutils.core import setup

from setuptools import find_packages


def requirements(fname):
    return [line.strip()
            for line in open(os.path.join(os.path.dirname(__file__), fname))]

setup(
    name="para",
    version="0.0.1",
    author="Aaron Halfaker",
    author_email="aaron.halfaker@gmail.com",
    packages=find_packages(),
    scripts=[],
    url="http://pypi.python.org/pypi/para",
    license=open("LICENSE").read(),
    description="a set utilities that ake advantage of python's " +
                "'multiprocessing' module to distribute CPU-intensive tasks",
    long_description=open("README.md").read(),
    install_requires=[],
    test_suite="nose.collector",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering"
    ],
)
