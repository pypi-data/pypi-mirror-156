# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pysquale",
    version="0.0.2",
    author="Henrique Santana",
    author_email="santana@cloudhumans.com",
    description="Useful lib for text processing in Portuguese",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pysquale.readthedocs.io/",
    project_urls={
        "Bug Tracker": "https://github.com/santana-ai/pysquale/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["pysquale"],
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        'nltk>=3.7',
    ],
)