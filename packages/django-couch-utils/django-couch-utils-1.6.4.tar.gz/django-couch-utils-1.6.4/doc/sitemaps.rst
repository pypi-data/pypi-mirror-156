Sitemaps
========


django.contrib.sitemaps requires the sites framework, which in turn requires a django-compatible database. django-couch-utils provides its own sitemaps framework to solve this problem.

So,

Configuration
-------------

settings.py::

  INSTALLED_PACKAGES = (
    ...
    'django_couch.sitemaps',
    ...
  )



urls.py::

  sitemaps = {
      'entry': YourFlatPageClass, 
  }

  urlpatterns = ...
      ...
      url(r'^sitemap\.xml$', 'django_couch.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
      ...

For more examples of FlatPageClass implementation, please refer to :ref:`flatpages`.


