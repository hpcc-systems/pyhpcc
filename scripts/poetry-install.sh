#!/bin/bash
python3 -m venv ${{vars.POETRY_HOME}}
${{vars.POETRY_HOME}}/bin/pip install poetry==1.2.0