import requests
import logbook
import json
import os
from pandas import DataFrame, Series

log = logbook.Logger('Forex')


def forex_rates(user, password, pairs='', fmt='csv'):
    auth = requests.get('http://webrates.truefx.com/rates/connect.html?&q=ozrates&c={}&f={}&s=n'
                        .format(','.join(pairs), fmt),
                        auth=('Gusabi', 'quantrade'))

    if auth.ok:
        log.debug('[{}] Request successful {}:{}'.format(auth.headers['date'], auth.reason, auth.status_code))
    #return auth.content.split('\n')[:-2]
    return auth.content.split('\n')


#FIXME 'Not authorized' mode works weird
class ConnectTrueFX(object):
    def __init__(self, user=None, password=None, auth_file='default.json', pairs='', fmt='csv'):
        #NOTE Without authentification you still can acess some data
        #FIXME Not authorized response prevent from downloading quotes. However later you indeed retrieve 10 defaults
        self._code = None
        if (user is None) or (password is None):
            log.info('No credentials provided, trying to read configuration file')
            try:
                config   = json.load(open('/'.join([os.path.expanduser('~/.quantrade'), auth_file]), 'r'))['truefx']
                user     = config['user']
                password = config['password']
            except:
                log.error('** Loading configuration file, no authentification will be used')
                user = password = ''

        auth = requests.get('http://webrates.truefx.com/rates/connect.html?u={}&p={}&q=ozrates&c={}&f={}'
                            .format(user, password, ','.join(pairs), fmt))
        if auth.ok:
            log.debug('[{}] Authentification successful {}:{}'.format(auth.headers['date'], auth.reason, auth.status_code))
            log.debug('Got: {}'.format(auth.content))

        ### Remove '\r\n'
        self._code = auth.content[:-2]

    def QueryTrueFX(self, pairs='', fmt='csv'):
        if isinstance(pairs, str):
            pairs = [pairs]
        response = requests.get('http://webrates.truefx.com/rates/connect.html?id={}&f={}&c={}'
                                .format(self._code, fmt, ','.join(pairs)))

        mapped_data = self._fx_mapping(response.content.split('\n')[:-2])
        if len(mapped_data) == 1:
            return Series(mapped_data)
        return DataFrame(mapped_data)

    def _fx_mapping(self, raw_response):
        dict_data = dict()
        for pair in raw_response:
            pair = pair.split(',')
            #FIXME Timestamp = year 45173
            dict_data[pair[0]] = {'TimeStamp': pair[1],
                                  'Bid.Price': float(pair[2] + pair[3]),
                                  'Ask.Price': float(pair[4] + pair[5]),
                                  'High': float(pair[6]),
                                  'Low': float(pair[7])}
        return dict_data

    def isActive(self):
        return isinstance(self._code, str) and (self._code != 'not authorized')

    def __del__(self):
        #TODO Deconnection
        pass
