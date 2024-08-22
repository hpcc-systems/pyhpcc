# PyHPCC

[![Coverage badge](https://github.com/amila-desilva/pyhpcc-internal/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/amila-desilva/pyhpcc-internal/tree/python-coverage-comment-action-data)



PyHPCC is a Python package and wrapper built around the [HPCC Systems](https://hpccsystems.com/) web services that facilitate communication between Python and HPCC Systems. 
# Features
Some core functionalities PyHPCC supports are
1. Work Unit submission through inline queries or using a Git Repository.
2. Reading contents from a Logical file.
3. Uploading/Downloading files to a landing zone
4. Spray fixed and variable files
5. Making Roxie calls.
## ⚙️ Installation

### Prerequisites

To use PyHPCC, you need these the following installed on your system<br>
1. [Python3](https://www.python.org/downloads/)
2. [ECL Client Tools](https://hpccsystems.com/download/): Select your operating systems to download client tools

Before you install PyHPCC, please make sure you have ECL client tools installed on your machine. The method for installing client tools varies on Windows and Linux systems.


### Windows
#### ADDING ECL CLIENT TOOLS TO SYSTEM ENVIRONMENT VARIABLES
Installing ECL IDE on a Windows machine installs ECL Client Tools by default--it need not be installed separately. The path to the Client Tools needs to be added to the Windows Environment Variables:
  1. On the Windows search bar, type <em>environment variables</em> and select <em>Edit the system environment variables</em>.
  2. In the resulting window, click the <em>Environment Variables...</em> button at the bottom.
  3. Under the <em>System variables</em> block, double-click on the <em>Path</em> variable.
  4. Add the Client Tools path under the Path variable. The path looks like this: `C:\Program Files\HPCCSystems\<version>\clienttools\bin.` 
  5. Open a Command Prompt window, and type `ecl --version` to test if ECL Client Tools are accessible through the command line.
   <br>**NOTE**: if you had a Command Prompt or VS Code window open while editing the Environment Variables, you must re-open the window to allow the new changes to be picked up.


### Linux
#### ADDING ECL CLIENT TOOLS TO SYSTEM ENVIRONMENT VARIABLES
The ECL Client Tools must be installed separately on Linux machines from the [HPCC System's Download webpage](https://hpccsystems.com/download). Select a version of your choice. 
<br>
<!-- **NOTE**: Version 7.4.32 has been tested and used on Ubuntu. Version 6.4.12 has been tested and used on CentOS systems. -->


#### Client Tools Installation on Ubuntu
Download ECL Client Tools onto the Ubuntu machine. Then, run the following commands on a shell or bash window:

    apt-get update -y
    apt-get -f install


#### Client Tools Installation on CentOS
Download ECL Client Tools onto the CentOS machine. Then, run the following commands on a shell or bash window:

    yum clean all
    rm -rf /var/cache/yum
    yum -y install hpcc_clienttools_<version>_centos.rpm

#### PyHPCC Install
Download the latest stable build for `PyHPCC` from releases in GitHub.<br>

``` bash
pip install pyhpcc-<version>.tar.gz
#or
pip install pyhpcc-<version>-py3-none-any.whl
```

## 🚀 Quick Start
See the following [example](examples/work_unit_hello_world.py) to compile and run a work unit to output `Hello World` using inline queries with PyHPCC.

If you would like more examples, please check the [examples](examples) folder.


## For Contributors
Contributions to PyHPCC are welcomed and encouraged.<br>
Please have a look at [CONTRIBUTING.md](CONTRIBUTING.md) for specific contribution guidelines.


## License

This project is licensed under [Apache License 2.0](LICENSE)

<!-- For more information about the package, please refer to the detailed documentation - https://upgraded-bassoon-daa9d010.pages.github.io/build/html/index.html -->
