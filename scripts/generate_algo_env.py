#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 xavier <xavier@laptop-300E5A>
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


'''QuanTrade.

Usage:
  generate_algo_env.py --author=<name> --strategie=<name> [--manager=<name>] [--year=<xxxx>]
  generate_algo_env.py (-h | --help)
  generate_algo_env.py --version

Options:
  -h --help           Show this screen.
  --version           Show version.
  --author=<name>     Author of the algorithm
  --strategie=<name>  Strategie name
  --manager=<name>    Manager name
  --year=<xxxx>       Current year for copyright [default: 2013].

'''


import os
from docopt import docopt
import jinja2
import logbook
log = logbook.Logger('Generator')


def generate_from_template(completion, tpl_file, out_file=None):
    templates_path = '/'.join((os.environ['QTRADE'], 'config/templates'))

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_path))
    template = env.get_template(tpl_file)
    log.info('Rendering template')
    document = template.render(completion)

    if out_file:
        log.info('Writing tempalte to {}'.format(out_file))
        with open(out_file, 'w') as fd:
            fd.write(document)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='New algorithm environment generator')

    completion = {'author': arguments['--author'],
                  'strategie': arguments['--strategie'],
                  'year': arguments['--year']}
    print(completion)
    generate_from_template(completion,
                           'strategie.tpl'
                           '/'.join((os.environ['QTRADE'],
                                     'neuronquant/algorithmic/strategies',
                                     'test.py')))
