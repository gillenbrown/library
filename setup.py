from setuptools import setup, find_packages

setup(
	name="library",
	version="0.0.1",
	author="Gillen Brown",
	author_email="gillenbrown@gmail.com",
	packages=find_packages(exclude=["testing"]),
	install_requires=["ads"],
    tests_require=["pytest",
                   "python-coveralls"],
    test_suite="pytest"
	)
