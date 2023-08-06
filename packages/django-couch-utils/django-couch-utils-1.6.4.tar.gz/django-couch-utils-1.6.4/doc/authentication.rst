Authentication backend
======================

You may use django-couch-utils as django authentication backend. This is very simple and convenient.

Configuration
-------------

::

  settings.INSTALLED_APPS=(
  ...
      'django_couch.auth',
  )

  settings.AUTHENTICATION_BACKENDS = (
      'django_couch.auth.backend.CouchBackend',
  )
  
  COUCHDB_AUTH_DB = 'db' # key to settings.COUCHDB
  COUCHDB_AUTH_VIEW = 'users/admins' # auth view name
  COUCHDB_AUTH_ADMIN_LAMBDA = lambda user: getattr(user, 'is_staff', False) # auth view extended filter

Next, you need to create an apropriate view. The view must emit ``username`` as a key and a salted ``password`` hash as a value.
Example::

  function(doc) {
      if ((doc.type == 'user') && (doc.admin)) {
          emit(doc.username, doc.password);
      }
  }


The password format should be the same as that in django.auth.users backend.


Users API
---------

django-couch-utils authentication backend provides a user document as a User object:


.. autoclass:: django_couch.auth.models.User
   :members:

