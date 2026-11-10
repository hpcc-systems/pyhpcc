WsSQL2 SQL driver
=================

PyHPCC includes a read-only Python DB-API 2.0 driver for HPCC Systems' WsSQL2 service.
It uses the existing ``Auth`` object for the HPCC host,
protocol, and credentials.

Connect and query
-----------------

.. code-block:: python

   from pyhpcc.models.auth import Auth
   from pyhpcc.sql import connect

   auth = Auth("my-hpcc.example.com", "8010", "user", "password", protocol="http")
   with connect(auth) as connection:
       with connection.cursor() as cursor:
           cursor.execute(
               "SELECT id, name FROM hpcc_scan('regress::local::people')"
           )
           for row in cursor:
               print(row)

The default WsSQL2 endpoint is ``http://<host>:8510/WsSQL2`` and the WsDfu
metadata endpoint is ``http://<host>:8010/WsDfu/DFUQuery.json``. HTTPS uses
ports 18510 and 18010 respectively. The ``Auth.port`` value remains available
to other PyHPCC APIs and is not used as the SQL service port. For nonstandard
deployments, provide ``sql_url`` and/or ``dfu_url`` to ``connect``:

.. code-block:: python

   connection = connect(
       auth,
       sql_url="https://my-hpcc.example.com:9443/WsSQL2",
       dfu_url="https://my-hpcc.example.com:9444/WsDfu/DFUQuery.json",
       connect_timeout=30,
       read_timeout=300,
   )

Timeouts are in seconds. ``read_timeout=None`` (the default) waits without a
client-side read timeout. HTTPS certificate verification uses the standard
``requests`` trust configuration.

Query behavior
--------------

Only read-only queries are supported. A cursor streams results forward-only;
``arraysize`` controls the default ``fetchmany`` count, while
``cursor.set_fetch_size(rows)`` controls the WsSQL2 page size (zero uses the
server default). ``cursor.set_max_rows(rows)`` caps returned rows, and
``cursor.set_query_timeout(seconds)`` applies a timeout to query requests.
``cursor.cancel()`` cancels the active server cursor and can be called from
another thread.

Semicolon-separated scripts are split by WsSQL2 and executed one statement at
a time. ``cursor.nextset()`` advances to the next result set and closes the
previous server cursor. A syntax error in the script is reported before its
first statement runs; later execution errors stop the remaining script.

``connection.get_tables(pattern, types)`` lists logical files, and
``connection.get_columns(table_pattern, column_pattern)`` describes their
fields. Use ``%`` and ``_`` as wildcards. Result rows are tuples and
``cursor.description`` follows the DB-API 2.0 seven-field format.

Value types include Python ``int`` (including large integers), ``decimal.Decimal``,
``float``, ``bool``, ``str``, ``datetime.date``, ``datetime.time``,
``datetime.datetime``, ``uuid.UUID``, ``bytes``, and nested JSON-compatible
lists/dictionaries, according to the WsSQL2 column type. Invalid conversions
raise ``DataError``.

Limitations
-----------

Transactions are not supported; connections are always in autocommit mode.
Data modification and DDL are unsupported. Parameter binding and ``executemany``
are not supported; passing non-empty parameters raises ``NotSupportedError``.
Result sets are forward-only and read-only.

Testing
-------

Run the SQL driver unit tests with ``poetry run pytest tests/test_sql_driver.py``.
Include live integration tests with
``poetry run pytest tests/test_sql_driver.py --run-integration``.
The live integration tests use local WsSQL2 and WsDfu services at ports 8510
and 8010 by default, and scan the available ``regress::`` logical files.
Override the endpoints with ``PYHPCC_SQL_URL`` and ``PYHPCC_DFU_URL``. For
secured services, set ``HPCC_USERNAME`` and ``HPCC_PASSWORD``.
