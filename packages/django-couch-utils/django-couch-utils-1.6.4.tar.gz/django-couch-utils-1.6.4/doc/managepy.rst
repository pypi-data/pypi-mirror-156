CouchDB backup/restore tool
===========================

Editing view/show/list/filter/... functions in Futon might be painful, so I prefer editing it on disk. Also I usually manage my data with VCS (e.g. Mercurial). So why not have a tool helping us to synchronize between disk and database?

Configuration
-------------

Choose some directory where you'd like to store your couchdb design document. I prefer a folder named ``couchdb-design-docs`` in my project root folder (near manage.py script). All examples will use this assumption.

Directory structure must be like the following:

For view functions::

  document-name.language-extension/views/function_name/map.language-extension
  and
  document-name.language-extension/views/function_name/reduce.language-extension

For filters and shows function::

  document-name.language-extension/filters/function_name.language-extension

Example::

  auth.js/views/users/map.js
  pages.js/views/list/map.js



Using tool
----------

Help text::

  $ ./manage.py help couch
  Usage: manage.py couch [options] 

  Backup and restore couchdb database. Usage: ./manage.py couch [restore|backup]

  Options:
    -v VERBOSITY, --verbosity=VERBOSITY
                          Verbosity level; 0=minimal output, 1=normal output,
                          2=all output
    --settings=SETTINGS   The Python path to a settings module, e.g.
                          "myproject.settings.main". If this isn't provided, the
                          DJANGO_SETTINGS_MODULE environment variable will be
                          used.
    --pythonpath=PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
    --traceback           Print traceback on exception
    -f, --force           Real run (change target data)
    -s SERVER, --server=SERVER
                          Server address
    -d DATABASE, --database=DATABASE
                          Database name
    -p PATH, --path=PATH  Working directory
    -n DBKEY, --name=DBKEY
                          Database key (from settings.py). Will override
                          --server and --database arguments
    -r, --delete          Delete exceed items from database during restore
    --version             show program's version number and exit
    -h, --help            show this help message and exit



Examples
--------

1. Dump design documents from named (``-n``) database (defined in ``settings.COUCHDB['db1']``) to directory ``couchdb-design-docs/_backup``::

   $ ./manage.py couch backup -n db1 -p couchdb-design-docs

**Notice** : ``_backup`` will be automatically appended to disk path in backup run.


2. Dry run of restore design documents from disk onto database with checking exceed documents (``-r``)::

   $ ./manage.py couch restore -n db1 -p couchdb-design-docs -r

3. Real run (``-f``) of restore design documents from disk onto database with checking exceed documents (``-r``)::

   $ ./manage.py couch restore -n db1 -p couchdb-design-docs -r -f

4. Backup some database by its url to disk::

   $ ./manage.py couch backup -s http://node1:5984 -d some_database -p couchdb-design-docs


Setting default views path
--------------------------

Since 1.5.2, you can set default disk views path to simplify backup/restore::

   COUCHDB_VIEWS_DIR = '/path/to/project/couchdb-design-docs'

   COUCHDB = {
       'somename': {
           'server': 'http://localhost:5984',
           'database': 'dbname',
           'default': True,
       }
   }

Now, you can just run::

   $ ./manage.py couch restore -n somename

And script will use design docs from path ``/path/to/project/couchdb-design-docs/somename``.

Or you can define exact path for any database::

   COUCHDB = {
       'somename': {
           'server': 'http://localhost:5984',
           'database': 'dbname',
           'default': True,
           'path': '/path/to/project/couchdb-design-docs/different-path'
       }
   }

And script will use design docs from path ``/path/to/project/couchdb-design-docs/different-path``.

