#!/usr/bin/env python
#
# Copyright 2012 Xavier Bruhiere
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

#NOTE plac is cool but is an other dependency, should replace by optparse
import plac
import logbook
log = logbook.Logger('Database::Manager')

from neuronquant.data.database import Manager


@plac.annotations(
    symbols=plac.Annotation("Add provided stocks to db", 'option', 'a'),
    sync=plac.Annotation("Update quotes stored in db", 'flag', 's'),
    create=plac.Annotation("Create database from written models", 'flag', 'c'))
def main(sync, create, symbols=None):
    ''' MySQL Stocks database manager '''
    db = Manager()

    if create:
        log.info('Creating database...')
        db.create_database()

    elif sync:
        log.info('Synchronizing quotes database...')
        db.sync_quotes()

    else:
        log.info('Adding new stocks in database...')
        assert symbols
        if symbols.find('csv') > 0:
            db.add_ticker_from_file(symbols)
        elif symbols.find(',') > 0:
            stocks = symbols.split(',')
            for ticker in stocks:
                db.add_ticker(ticker)
        else:
            db.add_ticker(symbols)
    log.info('Done')


if __name__ == '__main__':
        plac.call(main)
