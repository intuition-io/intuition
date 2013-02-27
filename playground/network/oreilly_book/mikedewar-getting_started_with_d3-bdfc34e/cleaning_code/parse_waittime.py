import xml.dom.minidom
import json
import pandas
import datetime
from operator import itemgetter
import time

# For this example we had to load and parse the NYCT Performance XML file.

# Essentially, we need to parse the XML, pull out the indicators we want, and
# then save them to a JSON which is much easier to play with in javascript.

# For this particular example, we are actually using two JSON files, which will
# be loaded separately. The second JSON is the mean of data in the first, so we
# need only parse the XML once.

# data available at http://www.mta.info/developers/data/Performance_XML_Data.zip

# use the minidom to parse the XML.
dom = xml.dom.minidom.parse('Performance_NYCT.xml')
# pull out all the indicators in the XML
indicators = dom.documentElement.getElementsByTagName('INDICATOR')

# this is a little function that just gets the data out of a particular indicator.
# it just saves us a bit of typing...
def get(indicator, name):
    return indicator.getElementsByTagName(name)[0].childNodes[0].data

# we only want those wait assessments associated with a specific line, so
# we include that extra "-" which doesn't appear in other indicator names
to_pull = 'Subway Wait Assessment -'
# initialise the list that we will dump to a JSON
out = []
for indicator in indicators:
    # if this is the right sort of indicator...
    if to_pull in indicator.getElementsByTagName('INDICATOR_NAME')[0].childNodes[0].data:
        try:
            # we get the name first as we need to use it for display, but reverse 
            # it for the #id
            name = get(indicator, 'INDICATOR_NAME').split('-')[1].strip()
            # we can't use CSS selectors that start with a number! So we gotta
            # make something like line_2 instead of 2_line.
            line_id = name.split(' ')
            line_id.reverse()
            line_id = '_'.join(line_id)
            # the time index here is month and year, which are in separate tags for
            # some reason, making our lives uncessarily complicated
            month = get(indicator, 'PERIOD_MONTH')
            year = get(indicator, 'PERIOD_YEAR')
            # note that the timestamp is in microseconds for javascript
            timestamp = int(time.mktime(
                datetime.datetime.strptime(month+year,"%m%Y").timetuple()
            )) * 1000 
            out.append({
                "line_name": name,
                "line_id": line_id,
                "late_percent": float(get(indicator, 'MONTHLY_ACTUAL')),
                "time": timestamp,
            })
        except IndexError:
            # sometimes a tag is empty, so we just chuck out that month
            pass

# filter out zero entries
out = [
    o for o in out if o['late_percent'] 
    if 'S' not in o['line_name']
    if 'V' not in o['line_name']
    if 'W' not in o['line_name']
]
# dump the data
json.dump(out, open('../viz/data/subway_wait.json','w'))

# compute the mean per line (easy with pandas!)
# build the data frame
df = pandas.DataFrame(out)
# groupby line and take the mean
df_mean = df.groupby('line_name').mean()['late_percent']
# build up the JSON object (one day pandas will have .to_json())
out = [
    {"line_id":'_'.join(reversed(d[0].split(' '))), "line_name":d[0], "mean": d[1]} 
    for d in df_mean.to_dict().items()
]
out.sort(key=itemgetter('line_name'))
# dump the data
json.dump(out, open('../viz/data/subway_wait_mean.json','w'))