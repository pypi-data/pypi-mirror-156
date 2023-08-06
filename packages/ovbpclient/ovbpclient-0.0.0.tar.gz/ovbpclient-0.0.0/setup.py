from setuptools import setup, find_packages
from pkg_resources import parse_requirements
import os

REPO_NAME, PACKAGE_NAME = "ovbpclient", "ovbpclient"

with open(os.path.join(PACKAGE_NAME, "version.py")) as f:
    version = f.read().split("=")[1].strip().strip("'").strip('"')

with open("requirements.txt", "r") as f:
    requirements = [str(r) for r in parse_requirements(f.read())]

setup(
    name=PACKAGE_NAME,
    version=version,
    packages=find_packages(exclude="tests"),
    author="Openergy team",
    author_email="contact@openergy.fr",
    long_description=open("README.md").read(),
    install_requires=requirements,
    url=f"https://github.com/openergy/{REPO_NAME}",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Natural Language :: French",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.1",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    package_data={PACKAGE_NAME: []},
    include_package_data=True
)
