#!/bin/bash
pipenv run python setup.py
pipenv run python app.py
pipenv run python teardown.py
