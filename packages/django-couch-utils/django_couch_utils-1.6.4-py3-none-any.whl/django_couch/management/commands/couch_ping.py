#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from django.core.management.base import BaseCommand
from django.conf import settings

import django_couch
#from optparse import make_option

import multiprocessing

## class Pinger(multiprocessing.Process):
##     def __init__(self, verbosity, db_key, view_name, func_name):
##         multiprocessing.Process.__init__(self)

##         self.verbosity = verbosity
##         self.db_key = db_key
##         self.view_name = view_name
##         self.func_name = func_name

##     def run(self):
##         db = django_couch.db(self.db_key)
##         if self.verbosity >= 2:
##             print('quering view %s/%s' % (self.view_name, self.func_name))
##         db.view('%s/%s' % (self.view_name, self.func_name), limit=0).rows


class Command(BaseCommand):

    help = u'Requests all couchdb views. Usage: ./manage.py couch_ping <db>, where <db> is couchdb definition from settings.py'

    def add_arguments(self, parser):
        parser.add_argument('db', nargs='*', type=str, help='DB keys to ping. If omitted, all dbs from settings will be pinged')
        parser.add_argument('--sync', action='store_true', help='Wait each view until ready (sync mode)')

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity'))

        workers = []

        dbs = options['db']
        if not dbs:
            dbs = settings.COUCHDB.keys()

        for db_key in dbs:
            if verbosity > 1:
                print("Using database %s" % db_key)
                print("Settings data: %s" % settings.COUCHDB[db_key])

            db = django_couch.db(db_key)

            for row in django_couch.design_docs(db):

                if verbosity > 1:
                    print("Design doc: %s" % row.id)

                view = row.id.split('/')[1]

                for function in row.doc.get('views', []):
                    if verbosity > 1:
                        print(db_key, view, function)

                    params = {
                        'limit': 1,
                    }

                    if not options['sync']:
                        params['stale'] = 'update_after'

                    if verbosity > 1:
                        print("Running %s/%s from %s" % (view, function, db_key))

                    r = django_couch.db(db_key).view('%s/%s' % (view, function), **params).rows

                    if verbosity > 1:
                        print("Done")


                    # we do need only first function from each design-doc
                    break
        if verbosity > 1:
            print('All done')
