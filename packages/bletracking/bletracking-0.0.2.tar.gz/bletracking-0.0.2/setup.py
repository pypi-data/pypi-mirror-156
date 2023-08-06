from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

setup(
    name="bletracking",
    version='0.0.2',
    author="jaytrairat",
    author_email="<jay.trairat@gmail.com>",
    description='bletracking',
    long_description_content_type="text/markdown",
    long_description='',
    packages=find_packages(),
    install_requires=[''],
    keywords=['jaytrairat'],
    classifiers=["Programming Language :: Python :: 3"]
)
