from setuptools import setup, find_packages

setup(
    name="library",
    version="0.0.1",
    author="Gillen Brown",
    author_email="gillenbrown@gmail.com",
    packages=find_packages(exclude=["testing"]),
    install_requires=["ads", "pyside6", "darkdetect", "bibtexparser"],
    extras_require={"test": ["pytest", "pytest-qt", "coverage"]},
    python_requires=">=3.7",
)
