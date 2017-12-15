#!/bin/bash
pipenv run python livetest.py
pipenv run python app.py
pipenv run python teardown.py
