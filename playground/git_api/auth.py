# This sample joyfully taken from https://gist.github.com/973705

import requests

r = requests.get('https://api.github.com', auth=('Gusabi', 'nintend_O140'))

print r.status_code
print r.headers['content-type']
