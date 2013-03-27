#!/usr/bin/python
#encoding: utf-8

import requests
 
# Other services
#http://curlmyip.com
#http://ipaddr.me
#http://www.icanhazip.com

url = r'http://jsonip.com'
r = requests.get(url)
ip = r.json()['ip']
print 'Your public IP: %s' % ip
