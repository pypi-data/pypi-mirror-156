***********
 nt-sqlite
***********

.. image:: https://api.travis-ci.com/nutratech/nt-sqlite.svg?branch=master
    :target: https://travis-ci.com/github/nutratech/nt-sqlite

Python, SQL and CSV files for setting up portable nt-sqlite database.

See CLI:    https://github.com/nutratech/cli

Pypi page:  https://pypi.org/project/nutra

Building the database
#########################

Create the database with.

::

    make build

Verify the tables were populated and exist.

::

    make test

If everything looks good: commit, and update submodules in the ``cli`` repo.

.. important:: If you are committing database changes, add a line to
    ``sql/data/version.csv`` (``id=4`` is the latest in this case).

    +-----+----------+-------------+------------------+
    | id  | version  | created     | notes            |
    +=====+==========+=============+==================+
    | 1   | 0.0.0    | 2020-09-22  | initial release  |
    +-----+----------+-------------+------------------+
    | 2   | 0.0.1    | 2021-05-21  | bump version     |
    +-----+----------+-------------+------------------+
    | 3   | 0.0.2    | 2021-05-24  | remove guids     |
    +-----+----------+-------------+------------------+
    | 4   | 0.0.3    | 2021-05-24  | general cleanup  |
    +-----+----------+-------------+------------------+

Tables (Relational Design)
##########################

**Note:** functions are kept in ``sql/functions.sql``.

See ``sql/tables.sql`` for details on design.

This is frequently updated, see ``docs/`` for more info.

.. image:: docs/nt.svg
