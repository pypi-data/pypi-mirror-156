import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of README file
README = (HERE / "README.md").read_text()

# This is a call to setup does all setup works.
setup(
    name="simplecalq",
    version="0.0.1",
    description="simple python library to demonstrate python tooling",
    long_description=README,
    url="",
    author="BrainStorm",
    author_email="dhiraj@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
    packages=["calculator"],
    include_package_data=True,
    install_requires=["pandas"]
)