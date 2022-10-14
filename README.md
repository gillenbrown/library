[![Tests](https://github.com/gillenbrown/library/actions/workflows/tests.yaml/badge.svg)](https://github.com/gillenbrown/library/actions/workflows/tests.yaml)
[![Coverage Status](https://coveralls.io/repos/github/gillenbrown/library/badge.svg)](https://coveralls.io/github/gillenbrown/library)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Black Code Style](https://github.com/gillenbrown/library/actions/workflows/black-code-style.yaml/badge.svg)](https://github.com/gillenbrown/library/actions/workflows/black-code-style.yaml)


# library
An attempt to implement a citation manager (in the style of ADS Libraries or Mendeley) designed for astronomy.

# Installation

Before doing anything, please know that this application is a work in progress. If you find a bug or have a feature you'd like to be added, please email me! I'll be more than happy to work with you to fix any issues you're having. 

To start, you'll need an ADS key to be able for the application to connect with ADS. Follow the steps to generate a new key [here](https://github.com/adsabs/adsabs-dev-api#access) (just steps 1 and 2, don't worry about the `curl` command). Once you get that API key, save it as an environment variable named `ADS_DEV_KEY`. 

Then you can install the Pyton application. You'll need to be using Python 3. I haven't yet made a simple executable, so for now you'll need to clone the repository and install it with pip. This will install all the dependencies too.

```
git clone https://github.com/gillenbrown/library.git
pip install -e .[test]
```
I recommend including the `[test]` flag to install the dependencies needed to run the tests, so you can validate that everything is working on your system (note that if you use zsh, you'll need quotes: ```pip install -e ".[test]"```). To run the tests, navigate to the main repository directory and run 
```
python -m pytest
```
When the tests run, the interface may appear a few times, but that is temporary and part of the tests. The tests should all pass, but if they don't, reach out and I'll help you figure out what's going wrong. 

# Launching the Application

To run the application, simply run the `run.py` script: 
```
python run.py
```
You'll probably want to run this in a screen session or just move the process to the background to get your terminal back. 

# Acknowledgements
<a href="https://www.flaticon.com/free-icons/book" title="book icons">Book icons created by Icongeek26 - Flaticon</a>
