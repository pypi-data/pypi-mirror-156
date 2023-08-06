import os
from setuptools import setup, find_namespace_packages

with open("requirements.txt") as f:
    required = f.read().splitlines()

    setup(
        name="traxix.trixli",
        version="0.0.8",
        url="https://gitlab.com/trax/trixli",
        packages=find_namespace_packages(include=["traxix.*"]),
        install_requires=required,
        scripts=[
            "traxix/trixli/again",
            "traxix/trixli/pexor.py",
            "traxix/trixli/f",
            "traxix/trixli/fr",
            "traxix/trixli/fp",
            "traxix/trixli/fe",
            "traxix/trixli/ec2l",
        ],
        author="trax Omar Givernaud",
    )
