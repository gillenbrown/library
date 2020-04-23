from setuptools import setup, find_packages

setup(
	name="library",
	version="0.0.1",
	author="Gillen Brown",
	author_email="gillenbrown@gmail.com",
	packages=find_packages(),
	install_requires=["pytest",
					  "ads"]
	)
