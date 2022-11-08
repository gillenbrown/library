[![Tests](https://github.com/gillenbrown/library/actions/workflows/tests.yaml/badge.svg)](https://github.com/gillenbrown/library/actions/workflows/tests.yaml)
[![Coverage Status](https://coveralls.io/repos/github/gillenbrown/library/badge.svg)](https://coveralls.io/github/gillenbrown/library)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# Library - A citation manager designed for astronomy

This simple Python application is designed to make it easy to keep track of the astronomy literature. Some key features include:
- Add papers with the URL of the paper's page on either ADS or the arXiv
- Automatic queries to ADS to get all the paper's details, including the bibtex entry
- Automatic downloading of the paper PDF
- Open the paper PDF using your preferred local PDF viewer
- Papers on the arXiv that do not have full journal information will be automatically updated as soon as that information is available on ADS
- Papers can be organized into different groups using tags
- Export the bibtex entries for all papers, all papers belonging to a given tag, or just a single paper
- Space for notes on each paper

![alt text](library/resources/interface_demo.png?raw=true)

# Installation

Before doing anything, please know that this application is a work in progress. If you find a bug or have a feature you'd like to be added, please [email me](mailto:gillenbrown@gmail.com)! I'll be more than happy to work with you to fix any issues you're having. 

To start, you'll need an ADS key to be able for the application to connect with ADS. Follow the steps to generate a new key [here](https://github.com/adsabs/adsabs-dev-api#access) (just steps 1 and 2, don't worry about the `curl` command). Once you get that API key, save it as an environment variable named `ADS_DEV_KEY`. 

Then you can install the Pyton application. You'll need to be using Python 3. I haven't yet made a simple executable, so for now you'll need to clone this repository and install it with pip. This will install all the dependencies too. Because of this, if you use virtual environments (e.g. `venv` or `conda`) you may want to create a new environment. 

```
git clone https://github.com/gillenbrown/library.git
cd library
pip install -e .[test]
```
I recommend including the `[test]` flag to install the dependencies needed to run the tests, so you can validate that everything is working on your system (note that if you use zsh, you'll need quotes: ```pip install -e ".[test]"```). To run the tests, navigate to the main repository directory and run 
```
python -m pytest
```
When the tests run, the interface may briefly appear in several flashes, but that is temporary and part of the tests. These tests will take a few minutes. The tests should all pass (warnings are okay), but if they don't, reach out and I'll help you figure out what's going wrong. 

One particular way the tests may fail is an old version of the [sqlite3](https://docs.python.org/3/library/sqlite3.html) library (you'll see an assertion error coming from lines 9 or 10 of `database.py`). If you use anaconda, you can try `conda install sqlite`. If that doesn't resolve the issue, you may need to update your Python version, as sqlite3 is bundled with Python. Regardless, if you encounter this issue and have difficulty resolving it, please email me so we can figure it out together and I can improve these troubleshooting instructions.

# Launching the Application

To run the application, simply run the `run.py` script: 
```
python run.py
```
You'll probably want to run this in a screen session or just move the process to the background to get your terminal back. 

# Potential bugs to look out for

This application is a work in progress, and so far has only been tested by me, so there are likely bugs I haven't found yet. If you find that something doesn't work how you expect, or you have suggestions on how to make the application more functional or easier to use, please [email me](mailto:gillenbrown@gmail.com)! In particular, here are some things that I suspect may still need work:
- Occasionally I found papers with atypical attributes that break my code. I fixed all the issues with papers I've tried to add, but if you find that adding a certain paper fails, send me a link to that paper and I'll fix it.
- In the interface, I abbreviate some journal (e.g. MNRAS, ApJ). I got all the journals commonly used in the papers I've cited in my work, but of course that's not a representative sample. Let me know if there are any abbreviations I'm missing.
- I've written a system that updates arXiv papers with the full publication details once those are available. But my testing for this has been mostly contrived examples that may or may not be totally realistic, so keep an eye on your arXiv-only papers to see if the publication details are correctly updated.
- Downloading the paper PDFs works okay, but not great. It first tries to download the PDF from the publisher, but in my testing the publisher often blocks the download since it thinks it's a bot (which it really is, to be fair). The application uses the arXiv PDF as a fallback. But the publishers may block me in particular since I sent a lot of requests when testing. So I'd be interested in seeing how many publisher PDFs regular users are able to download.
- On a lighter note, I need a better name for this! "Library" has been a placeholder, so if you have any ideas for a name let me know.

# Acknowledgements
This would not be possible without the [ads library](https://github.com/andycasey/ads) maintained by Andy Casey, which uses the [ADS API](https://github.com/adsabs/adsabs-dev-api).

<a href="https://www.flaticon.com/free-icons/book" title="book icons">Book icons created by Icongeek26 - Flaticon</a>

<a href="https://www.flaticon.com/free-icons/dropdown-arrow" title="dropdown arrow icons">Dropdown arrow icons created by NextGen - Flaticon</a>
