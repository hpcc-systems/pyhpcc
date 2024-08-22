.. _readfile:

How to read files using :func:`ReadFileInfo.get_data_iter`  
===========================================================

The ``ReadFileInfo`` class provides various functionalities to work with Flat and CSV logical files


Let's see an example of how to read files.


.. code-block:: python
    :linenos:
    :emphasize-lines: 24-28, 30-32

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
    protocol = "http"  # Specify HTTP or HTTPS
    cluster = "thor"  # Specify the cluster name to be used
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

        for data_attr, data in read_file.get_data_iter(0, 10, 10):
            print(data_attr)
            print(data)

    except Exception as e:
        print(e)

``ReadFileInfo`` class requires a ``HPCC``, ``logical_file_name``

The above code will produce the following output


.. code-block:: bash

    {'start': 1, 'count': 10, 'requested': 10}
    id first_name   last_name                   email      gender       ip_address
    0   1     Martyn  Millership  mmillership0@wired.com        Male  136.173.165.169
    1   2     Saidee  Martinelli   smartinelli1@imdb.com      Female   100.105.46.212
    2   3     Florri     Liggins  fliggins2@japanpost.jp      Female      15.48.63.74
    3   4   Vivianna       Older     volder3@blogger.com      Female     196.53.150.5
    4   5      Storm     Beswick  sbeswick4@google.co.jp      Female    84.252.95.111
    5   6   Gayelord      Raraty       graraty5@about.me        Male   146.170.229.15
    6   7     Harlen      Antill      hantill6@nymag.com        Male     23.201.93.96
    7   8     Arther  Smallpeace     asmallpeace7@cbc.ca        Male   250.173.182.85
    8   9       Dory     Roblett     droblett8@alexa.com        Male  148.253.132.231
    9  10      Hetty     D'Onise           hdonise9@g.co  Non-binary    113.40.121.87



.. py:function:: get_data_iter(start_index, items_size, batch_size)

    :param start_index: Specifies the index from which records needs to be fetched. The ``start_index`` starts from index 1 for csv files if ``infer_header`` is set to True in ``ReadFileInfo`` object initiation

    :param items_size: Specifies the number of records to be fetched. if -1, fetches until the end
   
    :param batch_size: Gets the data in batches of batch_size

    :returns: iterator: Python iterator yields data of ``batch_size``
    
    
.. code-block:: python

    for data_attr, data in read_file.get_data_iter(0, 10, 10):
        print(data_attr)
        print(data)


Every call to the iterator yields a tuple(data_attr, data). 

``data_attr`` contains info for the records fetched: **start**, **count**, **requested**, **total**

``data`` is a pandas DataFrame object of length ``batch_size``



Let's use a sample csv to show various use-cases with ``get_data_iter`` function

Lets assume our logical_file csv is ``pyhpcc::em::test::emp`` with the contents

.. code-block:: bash


   id first_name    last_name                            email   gender       ip_address
    0     Kelsey      Mateiko             kmateikoj@flavors.me   Female     42.238.83.81
    1      Anett    Eisenberg  aeisenbergk@creativecommons.org   Female   191.48.226.187
    2     Dannie        Tufts             dtuftsl@trellian.com     Male    180.68.44.244
    3      Mirna     Phillott              mphillottm@xing.com  Agender  161.194.215.229
    4      Noami  Christensen    nchristensenn@photobucket.com   Female  224.102.127.229
    5      Roley     Lorenzin        rlorenzino@eventbrite.com     Male   121.228.224.79
    6      Marlo       Ealden       mealdenp@printfriendly.com     Male    72.131.249.75
    7    Myranda        Matys                 mmatysq@tamu.edu   Female   28.104.217.147
    8     Gunner     Luchetti            gluchettir@dion.ne.jp     Male   167.33.240.147
    9     Willey       Bassom           wbassoms@google.com.br     Male   20.218.166.132

Let's retrieve all the records using the following code:

.. code-block:: python


    for data_attr, data in read_file.get_data_iter(0, -1, 10):
        print(data_attr)
        print(data)


The output of the file will be as follows

.. code-block:: bash


    {'start': 1, 'count': 10, 'requested': 10} # data_attr
    id first_name    last_name                            email   gender       ip_address
    0   0     Kelsey      Mateiko             kmateikoj@flavors.me   Female     42.238.83.81
    1   1      Anett    Eisenberg  aeisenbergk@creativecommons.org   Female   191.48.226.187
    2   2     Dannie        Tufts             dtuftsl@trellian.com     Male    180.68.44.244
    3   3      Mirna     Phillott              mphillottm@xing.com  Agender  161.194.215.229
    4   4      Noami  Christensen    nchristensenn@photobucket.com   Female  224.102.127.229
    5   5      Roley     Lorenzin        rlorenzino@eventbrite.com     Male   121.228.224.79
    6   6      Marlo       Ealden       mealdenp@printfriendly.com     Male    72.131.249.75
    7   7    Myranda        Matys                 mmatysq@tamu.edu   Female   28.104.217.147
    8   8     Gunner     Luchetti            gluchettir@dion.ne.jp     Male   167.33.240.147
    9   9     Willey       Bassom           wbassoms@google.com.br     Male   20.218.166.132

If you observe carefully, ``start`` attribute in ``data_attr`` is ``1`` instead of start_index ``0`` specified.

This is because ReadFileInfo class assumes that the header exists in the **0th** row. So it tries to fetch the records from index **1**. 
If you would like to override the behaviour set the ``infer_header`` flag during ``ReadFileInfo`` object initiation to False, instead of True (defualt) value.


Lets see an example on retrieving records with ``infer_header`` set to ``False``

.. code-block:: python

    read_file = ReadFileInfo(
        hpcc=hpcc_object, logical_file_name=logical_file, infer_header=False
    )
    for data_attr, data in read_file.get_data_iter(0, -1, 10):
        print(data_attr)
        print(data)


.. code-block:: bash


    {'start': 0, 'count': 10, 'requested': 10}
    0           1            2                                3        4                5
    0  id  first_name    last_name                            email   gender       ip_address
    1   0      Kelsey      Mateiko             kmateikoj@flavors.me   Female     42.238.83.81
    2   1       Anett    Eisenberg  aeisenbergk@creativecommons.org   Female   191.48.226.187
    3   2      Dannie        Tufts             dtuftsl@trellian.com     Male    180.68.44.244
    4   3       Mirna     Phillott              mphillottm@xing.com  Agender  161.194.215.229
    5   4       Noami  Christensen    nchristensenn@photobucket.com   Female  224.102.127.229
    6   5       Roley     Lorenzin        rlorenzino@eventbrite.com     Male   121.228.224.79
    7   6       Marlo       Ealden       mealdenp@printfriendly.com     Male    72.131.249.75
    8   7     Myranda        Matys                 mmatysq@tamu.edu   Female   28.104.217.147
    9   8      Gunner     Luchetti            gluchettir@dion.ne.jp     Male   167.33.240.147

   {'start': 10, 'count': 1, 'requested': 10}
       0       1       2                       3     4               5
    0  9  Willey  Bassom  wbassoms@google.com.br  Male  20.218.166.132


As you can see above, since the ``infer_header`` is set to ``False``, the returned DataFrame has no assumptions regarding the headers.



Let's try to fetch data with ``batch_size`` =2 with ``items_size`` =4. To put in simple terms, we are trying to retrieve 4 items with 2 items on every call.


.. code-block:: python

    read_file = ReadFileInfo(hpcc=hpcc_object, logical_file_name=logical_file)
    for data_attr, data in read_file.get_data_iter(0, 4, 2):
        print(data_attr)
        print(data)


The output should be as follows:

.. code-block:: bash

    {'start': 1, 'count': 2, 'requested': 2}
       id first_name  last_name                            email  gender      ip_address
    0   0     Kelsey    Mateiko             kmateikoj@flavors.me  Female    42.238.83.81
    1   1      Anett  Eisenberg  aeisenbergk@creativecommons.org  Female  191.48.226.187

    {'start': 3, 'count': 2, 'requested': 2}
       id first_name last_name                 email   gender       ip_address
    0   2     Dannie     Tufts  dtuftsl@trellian.com     Male    180.68.44.244
    1   3      Mirna  Phillott   mphillottm@xing.com  Agender  161.194.215.229


