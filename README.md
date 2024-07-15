# PyHPCC

Pyhpcc is a Python package that allows accessing HPCC-systems via Python.

PyHPCC is a Python package and wrapper built around the [HPCC Systems](https://hpccsystems.com/) web services that facilitate communication between Python and HPCC Systems. 
# Features
Some core functionalities PyHPCC supports are  
1. Work Unit submission through inline queries or using a Git Repository.
2. Reading contents from a Logical file.
3. Uploading files to a landing zone
4. Making Roxie calls.
## ⚙️ Installation

### Prerequisites

To use PyHPCC, you need these<br>
1. [Python3](https://www.python.org/downloads/)
2. [ECL Client Tools](https://hpccsystems.com/download/): Select your operating systems to download client tools



Download the latest stable build from releases in GitHub.<br>

``` bash
pip install pyhpcc-<version>.tar.gz
#or
pip install pyhpcc-<version>-py3-none-any.whl
```

## 🚀 Quick Start
See the following [example](examples/work_unit_hello_world.py) to OUTPUT `Hello World` with ECL.

For more examples, check the [examples](examples) folder.


## For Contributors
Contributions to PyHPCC are welcomed and encouraged.<br>
For specific contribution guidelines, please take a look at [CONTRIBUTING.md](CONTRIBUTING.md).


For more information about the package, please refer to the detailed documentation - https://upgraded-bassoon-daa9d010.pages.github.io/build/html/index.html
