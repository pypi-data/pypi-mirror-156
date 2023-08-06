from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'DPyramid'
LONG_DESCRIPTION = 'A package to print numbers, alphabet,special character in different shapes of triangle.'

# Setting up
setup(
    name="DPyramid",
    version=VERSION,
    author="Divya Prakash",
    author_email="dprakash050@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['arithmetic', 'math', 'pyramid ', 'python tutorial', 'tiangle '],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)