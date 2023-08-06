from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name = "hadder",
    version = "1.1",
    description = "Hydrogen adder for pdb protein files",
    long_description = long_description,
    long_description_content_type='text/markdown',
    license = "Apache 2.0 Licence",

    url = "https://gitee.com/dechin/hadder",
    author = "Dechin CHEN",
    author_email = "dechin.phy@gmail.com",
    packages = find_packages(exclude=["tests", "examples"]),
    install_requires=open('requirements.txt','r').readlines(),
    platforms = "any",
    scripts = [],
    include_package_data=True
)