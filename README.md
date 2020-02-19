# Toponym extraction

This repo contains some tools written in Python for extracting toponyms from newspaper articles downloaded from LexisNexis. Check out the [case study](https://lcvriend.github.io/toponym_extraction/) for an example. An interactive map can be found [here](https://lcvriend.github.io/toponym_extraction/map_toponyms.html).

The repo consists of scripts for:
- [Creating a spaCy NER-model for extracting toponyms](scripts/01_create_model.py)
- [Extracting text and meta data from LexisNexis files](scripts/02_textraction.py)
- [Applying the model to the text and extracting statistics from it](scripts/03_spacify)

Beyond that the repo contains several helper functions that can be used for data exploration/analysis in a notebook.
