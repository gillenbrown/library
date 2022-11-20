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

https://user-images.githubusercontent.com/12191474/201559494-a0fcbef5-cccf-4bb1-9cb1-a2d23dee25e5.mp4



# Installation

Before doing anything, please know that this application is a work in progress. If you find a bug or have a feature you'd like to be added, please [email me](mailto:gillenbrown@gmail.com)! I'll be more than happy to work with you to fix any issues you're having. 

To start, you'll need an ADS key to be able for the application to connect with ADS. Follow the steps to generate a new key [here](https://github.com/adsabs/adsabs-dev-api#access) (just steps 1 and 2, don't worry about the `curl` command). Once you get that API key, save it as an environment variable named `ADS_DEV_KEY`. 

Then you can install the Pyton application. You'll need to be using Python 3.7 or newer. I haven't yet made a simple executable, so for now you'll need to clone this repository and install it with pip. This will install all the dependencies too. Because of this, if you use virtual environments (e.g. `venv` or `conda`) you may want to create a new environment. 

```
git clone https://github.com/gillenbrown/library.git
cd library
pip install -e .[test]
```
I recommend including the `[test]` flag to install the dependencies needed to run the tests, so you can validate that everything is working on your system (note that if you use zsh, you'll need quotes: ```pip install -e ".[test]"```). To run the tests run this command from the main repository directory: 
```
python -m pytest
```
These tests will take a few minutes. The interface may briefly appear in several flashes, but that is temporary and part of the tests. The tests should all pass, but if they don't, reach out and I'll help you figure out what's going wrong. 

## Installation Troubleshooting

### ADS_DEV_KEY
If most (but not all) tests failed, you may not have set the ADS key correctly. To check, run `echo $ADS_DEV_KEY` in the terminal. If things are set up correctly, that command will output the string of random numbers and letters given to you by ADS. If not, make sure you're setting that as an environment variable.

### Duplicate Qt Libraries
If you encounter a fatal Python error after a handful of tests from `test_interface.py` run, you may have an issue with a duplicate version of `Qt` in your path (this is the library I use to create the GUI). This is installed by the pip install command above (bundled with the PySide6 library), but Python may be using a different version if you have a duplicate. In particular, this can happen if you use Anaconda to manage your Python environment. To check if this is the issue, run `conda list | grep qt`. If you see `qt` or `qt-main`, those are likely the issue. (Note that seeing `pytest-qt` is fine; that package is used for the tests). The simplest way to fix this is to create a new conda environment. If you're unfamiliar with these, they're basically a way to have self-contained Python installations ([see here](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) for more info). Here are the terminal commands to set this up:
```
conda create -n library python=3
conda activate library
```
The first command will prompt to you to install some libraries, then the second will activate the new Python environment. Then in that fresh environment, we can install and test as normal:
```
pip install -e .[test]
python -m pytest
```
Whenever you're done with the library (either just the tests or the actual usage), you'll want to deactivate the environment to get back to your default Python evironment with `conda deactivate`. 

# Launching the Application

To run the application, simply run the `run.py` script: 
```
python run.py
```
You'll probably want to run this in a screen session or just move the process to the background to get your terminal back. 

# User Guide

To add papers to the database, you'll need copy a link to the paper from either ADS or the arXiv into the search bar at the top of the interface. For example, the following three links will all add the same paper: 
- https://ui.adsabs.harvard.edu/abs/2021MNRAS.508.5935B/abstract
- https://arxiv.org/abs/2106.12420
- https://arxiv.org/pdf/2106.12420.pdf

No matter which of the three links you use, the full paper details will be obtained from ADS. The one exception is papers on the arXiv that are not yet published. In this case, the code will keep an eye out for the full paper details on ADS. This means you can add a paper you find in the daily arXiv email, and the code will pull the full paper details once those are available without any input from you. Note that this check happens at launch no more than once every 24 hours. This check can take a slight bit of time (in my testing about 0.5 seconds per paper), so if there's a delay in opening the interface this may be the reason. 

One final note here is that sometimes ADS takes a bit of time to get the daily arXiv papers into its system. Since my code relies on ADS, sometimes the most recent arXiv papers will fail when you try to add them. You may need to try to add them later that day or tomorrow. 

### Paper Details

Once you add papers, you can click on them in the center panel to show their details in the right panel. It shows the title, journal info, then the abstract. Below that, there are several other actions you can take on this paper. Note that you can resize this (and other panels) by clicking and dragging on the separator. You can also collapse each panel entirely by dragging to the edge.

First, there is a place for you to take notes on the paper. When you're editing, you can click the "Done Editing Notes" button to save the notes, or hit Escape to discard your changes.

Next, there are actions related to the PDF of the paper. If you have already downloaded the PDF, you can click "Choose a local PDF" to select an existing file on your machine. You can also try to get the code to download a PDF for you. This will first try to download the publisher version of the PDF, but this may be blocked by paywalls (or systems that identify this code as a bot). If the publisher PDF fails, it will download the arXiv PDF. Either way, you'll be prompted to select a place to save this PDF. Once you have a PDF set for a paper, you can open that PDF in your native PDF viewer by clicking the button or double clicking on the paper in the center panel.

After the PDF, there's a section to set the tags of this paper. I'll talk about tags more in the next section of this guide, but here you can edit the tags assigned to this paper.

Next, there are actions related to the BibTeX entry for this paper. Here, you can modify what I call the "citation keyword" for the paper. This is the key you put inside the `\cite` keyword when citing a paper in LaTex, like so: `\citet{brown_etal_22}`. When writing papers, I prefer to modify these to be human friendly, and this allows that. Note that these keys are required to be unique. When editing this citation keyword, you can hit Escape to exit without saving, or enter an empty string to reset the citation keyword to the default, which is the bibcode assigned by ADS.

Finally, there is a button to open the paper's page in ADS, and a button to delete this paper. It will ask you to confirm before you delete it. 

### Tags

The tag system allows you to organize your papers into groups. Each paper can have multiple tags. The left panel shows the list of tags. To show only the papers with a given tag, click on the name of the tag. When you add a new paper when a given tag is selected, the tag will be automatically applied to that paper.

As discussed above, you can edit the tags a given paper has after clicking it.  In the left panel you can also add new tags or delete existing ones. When entering the name of the tag to add or delete, you can exit without adding/deleting by pressing Escape or pressing backspace when the text field is empty. 

Whenever you have a tag selected in the left panel, there is an export button shown. When pressed, this saves a `.bib` file containing all the BibTeX entries for papers with this tag. This file can then be used directly in a LaTeX document.

### Dark Mode

On startup, the code will detect whether your OS is using dark or light mode, and match the interface theme accordingly. You can switch the theme by clicking the Library logo in the top left. 

### One final note...

All the data used in this application (including the list of papers, your user notes, the locations of the PDFs, and the tags assigned to each paper) are stored in a database in the code directory called `USER_DATA_DO_NOT_DELETE.db`. As the name suggests, you'll lose everything if you delete this file. You may want to keep it backed up. 

# Potential bugs to look out for

This application is a work in progress, and so far has only been tested by me, so there are likely bugs I haven't found yet. If you find that something doesn't work how you expect, or you have suggestions on how to make the application more functional or easier to use, please [email me](mailto:gillenbrown@gmail.com)! In particular, here are some things that I suspect may still need work:
- Occasionally I found papers with atypical attributes that break my code. I fixed all the issues with papers I've tried to add, but if you find that adding a certain paper fails, send me a link to that paper and I'll fix it.
- In the interface, I abbreviate some journal (e.g. MNRAS, ApJ). I got all the journals commonly used in the papers I've cited in my work, but of course that's not a representative sample. Let me know if there are any abbreviations I'm missing.
- I've written a system that updates arXiv papers with the full publication details once those are available. But my testing for this has been mostly contrived examples that may or may not be totally realistic, so keep an eye on your arXiv-only papers to see if the publication details are correctly updated.
- Downloading the paper PDFs works okay, but not great. It first tries to download the PDF from the publisher, but in my testing the publisher often blocks the download since it thinks it's a bot (which it really is, to be fair). The application uses the arXiv PDF as a fallback. But the publishers may block me in particular since I sent a lot of requests when testing. So I'd be interested in seeing how many publisher PDFs regular users are able to download.
- The code should identify whether your OS is using dark mode, and adjust the interface theme appropriately. I've only been able to truly test this on my laptop running macOS. Let me know if this doesn't work on your machine. 
- On a lighter note, I need a better name for this! "Library" has been a placeholder, so if you have any ideas for a name let me know.

# Acknowledgements
This would not be possible without the [ads library](https://github.com/andycasey/ads) maintained by Andy Casey, which uses the [ADS API](https://github.com/adsabs/adsabs-dev-api).

<a href="https://www.flaticon.com/free-icons/book" title="book icons">Book icons created by Icongeek26 - Flaticon</a>

<a href="https://www.flaticon.com/free-icons/dropdown-arrow" title="dropdown arrow icons">Dropdown arrow icons created by NextGen - Flaticon</a>
