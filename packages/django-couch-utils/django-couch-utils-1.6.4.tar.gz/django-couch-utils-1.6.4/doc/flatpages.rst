.. _flatpages:

Flatpages Middleware
====================

It is almost the same as the default django.flatpages framework but uses couchdb for pages storage.

Configuration
-------------
::

  settings.MIDDLEWARE_CLASSES=(
    ...
    'django_couch.flatpages.middleware.FlatpageFallbackMiddleware',
  )

  settings.INSTALLED_APPS=(
    ...
    'django_couch.flatpages',
    ...
  )

  COUCHDB_FLATPAGES = 'pages/list' # named view


For every 404 response, framework calls a database view to get key == ``request.path``. So function ```pages/list``` must be like the following::

  function(doc) {
      if (doc.type == 'page') {
          emit(doc.url);
      }
  } 

A document is rendered into the ``static.html`` template by default. You may override it with the ``doc.template`` field.

Variable ``doc`` is added to the template context.


Known limitations
-----------------

#. Database must be named as ``db`` in the ``settings.COUCHDB`` dictionary

Example
-------
Document::

  {
    "title": "Index page",
    "url": "/",
    "body": "This is index page body",
    "keywords": "some,keywords,here",
    "content_type": "text/plain", # default is text/html
    "template": "my_another_static_template.html", # default is "static.html"
    "type": "page",
  }

Template (``static.html``):

.. sourcecode:: html

  <html>
      <head>
          <title>{{ doc.title }}</title>
          <meta name="keywords" content="{{ doc.keywords }}" />
      </head>
      <body>
          <h1>{{ doc.title }}</h1>
          {{ doc.body }}
      </body>
  </html>


Flatpages Sitemaps support
--------------------------

django-couch-utils' flatpages framework fully supports its own sitemaps framework.

Configuration
~~~~~~~~~~~~~

urls.py::

  from django_couch.flatpages.sitemaps import FlatPageSitemap
  sitemaps = {
      ...
      'flatpages': FlatPageSitemap,
      ...
  }

Your CouchDB database must consist of pages/attachments, which emit ``[page-last-update-date, page-url]`` as the ``key`` and a list of page attachments (or null) as the ``value``.

Example view function::

  function(doc) {
      if (doc.type == "page") {
          var attachments = [];
          if (doc._attachments) {
              for(key in doc._attachments) {
                  if (doc._attachments[key].content_type.indexOf('image/') == 0) {
                      attachments.push(key);
                  }
              }
          }
          emit([doc.date, doc.url], attachments);
      }
  }
