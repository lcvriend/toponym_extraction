# Toponym extraction

[![Case Study](https://img.shields.io/badge/Repo-case_study-blue)](https://lcvriend.github.io/toponym_extraction/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lcvriend/toponym_extraction/master?filepath=notebooks%2Fexplore_data.ipynb)  

This repo contains:
1. [Tools](#tools) for extracting toponyms (and lemmata) from newspaper articles downloaded from LexisNexis.
2. The [results](#results) that were collected with these tools for a research on toponyms in news on Brexit in Dutch newspapers.
3. A short write up on this [case study](https://lcvriend.github.io/toponym_extraction/). Check out the interactive map [here](https://lcvriend.github.io/toponym_extraction/map_toponyms.html).

## Workflow

<img src="docs/illustrations/workflow.svg" alt="Workflow">

## Tools
There are three main scripts that were used to generate the data for this case study. Each script contains further documentation on how they should be used:
- **Build NER model** :[Create a spaCy NER-model for extracting toponyms](scripts/01_create_model.py)
- **Build data set**: [Extract text and meta data from LexisNexis files](scripts/02_textraction.py)
- **Extract toponyms**: [Apply the model to the data set and extract statistics from it](scripts/03_spacify.py)

The `PhraseAnnotator` in [annotation_tools](src/annotation_tools.py) can be used to annotate the NER-results.

## Results
This tool currently extracts two main statistics for each geographical category defined in the [MODEL] chapter of [config.ini](config.ini):
1. Total frequency
2. Article counts

These scripts will generally store results in Python's [pickle](https://docs.python.org/3/library/pickle.html) format. In order to make the results of this study generally available the following data has been added to the repo as csv-files (some have been zipped):
1. The metadata for the [lexisnexis dataset](data/lexisnexis_dataset.csv)
2. The statistics of the [toponym recognition](results/toponym_results.gz)
3. The statistics of the [lemmata recognition](results/lemmata_results.gz)
4. The [annotation data](annotations)

The data and results have been made available through an online jupyter notebook. Access the notebook by clicking this button:  

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lcvriend/toponym_extraction/master?filepath=notebooks%2Fexplore_data.ipynb)

Use [pandas](https://pandas.pydata.org/pandas-docs/stable/index.html) and [altair](https://altair-viz.github.io/index.html) to explore the data.
