import xml.dom.minidom
import json
dom = xml.dom.minidom.parse('Performance_MTABUS.xml')
indicators = dom.documentElement.getElementsByTagName('INDICATOR')

pull = {
    'x':'Mean Distance Between Failures - MTA Bus',
    'y':'Collisions with Injury Rate - MTA Bus',
    'c':'Customer Accident Injury Rate - MTA Bus'
}

x = []
y = []
c = []

for indicator in indicators:
    try:
        name = indicator.getElementsByTagName('INDICATOR_NAME')[0].childNodes[0].data
        actual = indicator.getElementsByTagName('MONTHLY_ACTUAL')[0].childNodes[0].data
        actual = float(''.join(actual.split(',')))
    except IndexError:
        actual = None    
    
    if actual == 0.0:
        actual = None
    
    if name == pull['x']:
        x.append(actual)
    elif name == pull['y']:
        y.append(actual)
    elif name == pull['c']:
        c.append(actual)

out = []

for xi,yi,ci in zip(x,y,c):
    if xi is None or yi is None or ci is None:
        continue

    out.append({
        "dist_between_fail": xi,
        "collision_with_injury": yi,
        "customer_accident_rate": ci
    })

json.dump(out, open("../viz/data/bus_perf.json",'w'))
