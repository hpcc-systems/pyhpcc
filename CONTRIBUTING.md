# How to Contribute

We value your interest in contributing to `PyHPCC`

Thank you

## Setup the repository locally.
## Prerequisities
Before starting with developing, make sure you have the install the following software.
1. [Python3](https://www.python.org/downloads/)
2. [ECL Client Tools](https://hpccsystems.com/download/): Select your operating systems to download client tools
3. [Poetry](https://python-poetry.org/docs/#installation)

After installing the prerequisites, fork the repository.

```bash
git clone https://github.com/<your account name>/<repository name>.git
cd <repository name>
```
Set up the repository locally. Replace `<your account name>` with the name of the account you forked to and `<repository name>` with the repository name you forked.

To install the dependencies run the following command, which downloads the dependencies to your system and creates `poetry.lock` file.

``` bash
poetry install
```