#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#
# Copyright 2013 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import os
import argparse
from pprint import pprint
import sqlalchemy
import pickle
import csv


class ResultSet(list):
    def __init__(self, result):
        #import ipdb; ipdb.set_trace()
        # result.out_parameters()
        # result.rowcount
        if result.keys():
            for r in result:
                self.append(dict((a, b) for a, b in r.items()))
        else:
            self.append([])

    def export(self, filename, columns):
        #TODO automatic columns detection
        if type(filename) == file:
            f = filename
        else:
            f = open(filename, 'w')
        w = csv.DictWriter(f, columns)
        w.writeheader()
        w.writerows(self)
        f.close()


class Extractor(object):
    def __init__(self, url):
        self.engine = sqlalchemy.create_engine(url)

    def __call__(self, request):
        connection = self.engine.connect()
        result = ResultSet(connection.execute(request))
        connection.close()
        return result


class RequestManager(list):
    filename = 'request.pkl'

    def __init__(self):
        if os.path.isfile(self.filename):
            f = open(self.filename, 'rb')
            for d in pickle.load(f):
                self.append(d)
            f.close()
        else:
            print 'New cache file'

    def save(self):
        f = open(self.filename, 'wb')
        exported = []
        for d in self:
            exported.append(d)
        pickle.dump(exported, f)
        f.close()


def list_requests(namespace):
    manager = RequestManager()
    for r in manager:
        print('%(name)25s: %(sql)s' % r)


def append_request(namespace):
    manager = RequestManager()
    manager.append({'name': namespace.name, 'sql': namespace.content})
    manager.save()


def execute_request(namespace):
    manager = RequestManager()
    matching = [r['sql'] for r in manager if r['name'] == namespace.name]
    if len(matching) != 1:
        print 'Request was not found'
        return
    else:
        request = matching[0]
        try:
            extractor = Extractor(namespace.url)
        except:
            print 'URL provided is not valid or database is not running'
            return
        try:
            result = extractor(request)
        except:
            print 'Invalid request'
            return
        if namespace.export_filename is None:
            pprint(result)
        else:
            if len(result) == 0:
                print('No result to export')
                return
            if namespace.export_columns is None:
                columns = list(result[0].keys())
            else:
                columns = [unicode(c) for c in namespace.export_columns]
            result.export(namespace.export_filename, columns)
            print 'Done'


def getParser():
    parser = argparse.ArgumentParser(
        prog='./extractor.py',
        description='''Multi-database tool for a single request''',
        epilog='''Exemple designed for Linuxmag'''
    )
    subparsers = parser.add_subparsers(help='commands')
    list_parser = subparsers.add_parser(
        'list',
        # aliases=['l'],
        description='list of stored requests',
        help='List of available requests',
    )
    list_parser.set_defaults(func=list_requests)

    append_parser = subparsers.add_parser(
        'append',
        # aliases=['a', 'add'],
        description='Augment list of available requests adding a new one',
        help='Store a new request'
    )
    append_parser.add_argument(
        'name',
        help='Name of the request'
    )
    append_parser.add_argument(
        'content',
        help='Request'
    )
    append_parser.set_defaults(func=append_request)

    execute_parser = subparsers.add_parser(
        'execute',
        # aliases=['e', 'exec'],
        description='Execute a stored request (identified by name) on the database (identified by URL)',
        help='Execute one of available request on the database'
    )
    execute_parser.add_argument(
        'url',
        help='URL of database'
    )
    execute_parser.add_argument(
        'name',
        help='Name of the request'
    )
    execute_parser.add_argument(
        '-e', '--export',
        help='Name of CSV file',
        dest='export_filename',
        metavar='filename',
        type=argparse.FileType('w')
    )
    execute_parser.add_argument(
        '-c', '--columns',
        help='Name of columns of CSV file',
        dest='export_columns',
        metavar='columns',
        nargs='*'
    )
    execute_parser.set_defaults(func=execute_request)

    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
    args.func(args)
