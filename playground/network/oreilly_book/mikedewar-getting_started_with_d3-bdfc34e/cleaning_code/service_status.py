import json
import xmltodict as xml

# the xml file is available at http://www.mta.info/status/serviceStatus.txt
s = open("code/status.xml").read()
# we convert it to a dictionary
d = xml.xmltodict(s)
# and then dump the subway section into a JSON file to visualise
json.dump(d['subway'][0]['line'], open("../viz/data/service_status.json",'w'))