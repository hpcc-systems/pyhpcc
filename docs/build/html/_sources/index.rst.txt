.. PyHPCC documentation master file, created by
   sphinx-quickstart on Wed Oct 12 20:07:35 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyHPCC's documentation!
==================================
.. toctree::
   :maxdepth: 2

PyHPCC: helps you to interact with HPCC easier
=======================================

.. module:: pyhpcc

The ``PyHPCC`` framework makes interacting with HPCC Systems easier using Python.

``PyHPCC`` requires: Python 3.12+

A quick example
---------------

Let's write a program to check if a logical file exists

.. code-block:: python
   :linenos: 
   :emphasize-lines: 18-31

    # content of file_exists.py
   from pyhpcc.models.auth import Auth
   from pyhpcc.models.file import ReadFileInfo
   from pyhpcc.models.hpcc import HPCC

   # Configurations
   environment = (
      "university.us-hpccsystems-dev.azure.lnrsg.io"  # Eg: myuniversity.hpccsystems.io
   )
   port = "8010"  # Eg: 8010
   user_name = "user_name"  # HPCC username
   password = "password"  # HPCC password
   required_auth = True
   protocol = "http"  # Specify HTTP or HTTPS
   logical_file = "pyhpcc::testing::internet.csv"

   try:
      auth_object = Auth(
         environment,
         port,
         user_name,
         password,
         protocol=protocol,
      )
      hpcc_object = HPCC(auth=auth_object)
      read_file = ReadFileInfo(
         hpcc=hpcc_object,
         logical_file_name=logical_file,
      )

      print(read_file.check_file_in_dfu())  # Prints `True` if file exists else `False`

   except Exception as e:
      print(e)



To execute it:

.. code-block:: bash

    $ python file_exists.py
    True # If file exists
    # or
    False # If file doesn't exist

Let's run through the code.  

* A ``Auth`` object is created by passing HPCC environment url, port, username, password, protocol. Its used for authenticating to the hpcc system.
* A ``HPCC`` object is created which has implementations to configure timeout.
* A ``ReadFileInfo`` object is created for the file that you need to work with ``logical_file_name``, ``cluster``.
* Call the function ``check_file_in_dfu`` which returns ``True`` if file exists.


Features
--------

1. PyHPCC is a Python package and wrapper built around the HPCC Systems web services that facilitates communication between Python and HPCC Systems. 
2.  Read Logical file contents, retrieve subfiles, check file info.
3. Tools compile workunit, run inline and ecl workunit programatically using ECL client tools and wait on workunit until completion.
4. To help with upload/download files from landing zones, spray/despray files, read workunit info, compile and run workunits, retrieves workunit, get cluster info. 

Documentation
-------------
* :ref:`How-to guides <how-to>` - step-by-step guides, covering a vast range of use-cases and needs
* :ref:`Reference guides <pyhpcc_reference>` - includes the complete PyHPCC API reference


Bugs/Requests
-------------

Please use the `GitHub issue tracker <https://github.com/amila-desilva/pyhpcc-internal/issues>`_ to submit bugs or request features.