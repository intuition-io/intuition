import pandas
import json
import numpy as np

# import the data into a pandas table
df = pandas.read_csv('TBTA_DAILY_PLAZA_TRAFFIC.csv')

# make a little function that takes the terrible string
# in the CASH and ETC columns and converts them to an int
toint = lambda x: int(x.replace(',',''))

# convert both columns
df['ETC'] = df['ETC'].apply(toint)
df['CASH'] = df['CASH'].apply(toint)

# calculate the mean number of people paying cash
mean_cash = df.groupby("PLAZAID")['CASH'].aggregate(np.mean)
mean_etc = df.groupby("PLAZAID")['ETC'].aggregate(np.mean)

# build the key
key = { 
    1 : "Robert F. Kennedy Bridge Bronx Plaza",
    2 : "Robert F. Kennedy Bridge Manhattan Plaza",
    3 : "Bronx-Whitestone Bridge",
    4 : "Henry Hudson Bridge",
    5 : "Marine Parkway-Gil Hodges Memorial Bridge",
    6 : "Cross Bay Veterans Memorial Bridge",
    7 : "Queens Midtown Tunnel",
    8 : "Brooklyn-Battery Tunnel",
    9 : "Throgs Neck Bridge",
    11 : "Verrazano-Narrows Bridge"
}
# output to JSON we can use in d3
cash =  [
    {"id":d[0], "count":d[1], "name":key[d[0]]} 
    for d in mean_cash.to_dict().items()
]
electronic = [
    {"id":d[0], "count":d[1], "name":key[d[0]]} 
    for d in mean_etc.to_dict().items()
]

out = {
    "cash": cash, 
    "electronic": electronic 
}

json.dump(out, open('../viz/data/plaza_traffic.json', 'w'))
