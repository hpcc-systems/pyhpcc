#!/bin/bash
python3 -m venv $POETRY_HOME
$POETRY_HOME/bin/pip install poetry==1.8.3
$POETRY install