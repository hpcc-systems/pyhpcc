# How to Contribute

We value your interest in contributing to `PyHPCC.`

Thank you

- Check the issue tab for any issues that you would like to work on
- Comment on the issue showing your interest to work on the issue
- Raise a PR request to the repository and it will be reviewed for it to be merged. For more guidelines on creating a PR check [Submitting an PR](#submitting-an-pr) section.

## Project Structure
```
.
└── pyhpcc/
    ├── .github # contains build, release, test and other gh actions
    ├── docs/ # contains files for documentation
    ├── examples/ # contains starter examples
    ├── scripts # GitHub CI/CD Poetry install script
    ├── src/
    │   └── pyhpcc/
    │       ├── handlers/ # contains thor and roxie handler
    │       └── models/ # contains classes auth, workunit submit
    ├── tests/
    │   ├── models/
    │   ├── test_files/ # contains resource files needed for testing
    │   └── handlers/
    ├── pyproject.toml # Project config
    ├── MAINTAINING.md
    ├── CONTRIBUTING.md
    ├── README.md
    └── LICENSE
```

## Set up the repository locally.
## Prerequisites
Before starting to develop, make sure you install the following software:
1. [Python3](https://www.python.org/downloads/)
2. [ECL Client Tools](https://hpccsystems.com/download/): Select your operating systems to download client tools (More instructions to setup client-tools is mentioned in [README.md](README.md))
3. [Poetry](https://python-poetry.org/docs/#installation)

After installing the prerequisites, fork the repository.

```bash
git clone https://github.com/<your account name>/<repository name>.git
cd <repository name>
```
Set up the repository locally. Replace `<your account name>` with the name of the account you forked to and `<repository name>` with the repository name you forked.

To install the dependencies, run the following command, which downloads the dependencies to your system and creates a `poetry.lock` file.

``` bash
poetry install
```

## How to run tests  
Since ecl client tools aren't installed in the GitHub runner, some tests are skipped in the github runner.

Some tests will fail if `ecl client tools` aren't installed.

Create `my-secret.py` in project root and copy the contents of `my-secret-dummy.py`. Since, some of the tests require access to HPCC Cluster.

Running whole test suite

```
pytest # Run in project root
```

Running a specific test file

```
pytest tests/models/test_workunit_submit.py # /path/to/test_file
```

Running a specific test
```
pytest tests/models/test_workunit_submit.py::test_create_file # /path/to/test_file::test_name
```

## How to build docs
In the root folder after completing the installation setup:

Run the following command. This will rebuild Sphinx documentation on changes, with hot reloading in the browser.

``` bash
sphinx-autobuild docs/source docs/build # Builds the docs and creates a live server that reloads on changes
```

## Linting and Formatting
PyHPCC uses [Ruff](https://docs.astral.sh/ruff/) as its formatter and linter.

If you're using Visual Studio Code, install the ruff [extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

Before raising a pull request, make sure the code is formatted and lint errors are fixed using `ruff`.

You can also install `ruff` using pip

``` bash
pip install ruff
ruff check # For check any lint errors
ruff check --fix # Applies fix to resolve lint violations for safe fixes
ruff format # For formatting your code.
```


## PR Guidelines
For test coverage, please make sure to have more than 85% code coverage for both the individual and overall.
To check code coverage, run the following commands
``` bash
poetry run coverage run
poetry run coverage report
```



## Submitting an PR
[Create a PR](https://help.github.com/articles/creating-a-pull-request/) with the following configuration:
- Create a feature branch with the name `features/<issue_id_to_be_fixed>_<short description>` from the `dev` branch
- Commit your changes and push the changes to your fork.
- Create a PR to the `dev` branch
- PR name: copy-and-paste the relevant issue name and include the issue number in front in square brackets, e.g. `[#1020] Make bash_runcommand in WorkUnitSubmit class configurable `
- PR description: mention the issue number in this format: Fixes #1020. Doing so will automatically close the related issue once the PR is merged.
- Please Ensure that "Allow edits from maintainers" is ticked.
- Please describe the changes you have made in your branch and how they resolve the issue.
- Ensure code code coverage is above 85% for file and overall
- Once PR is raised, check if any checks are failing. Please fix these issues. Pull Requests will not be reviewed if any checks are failing.
- Make changes mentioned by reviewer.