#!/bin/bash
export NEW_CONTRACT_CODING_LOCAL="true"
pipenv run python livetest.py
pipenv run python app.py
pipenv run python teardown.py

# this needs to be SOURCED not just ran, in order to work with the env variable.
