from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = []

setup(
    name="aiohttp_clean_jwt",
    version="0.1.1",
    author="Vladimir Kirievskiy",
    author_email="vladimir@kirievskiy.ru",
    description="jwt authentication for aiohttp",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitflic.ru/project/vlakir/aiohttp-clean-jwt.git",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Scientific/Engineering"
    ],
)
