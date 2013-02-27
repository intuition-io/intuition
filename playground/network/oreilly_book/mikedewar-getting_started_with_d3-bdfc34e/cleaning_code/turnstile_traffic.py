import json
import datetime
import pandas

"""
This is the cleaning code for the turnstile data. 

The turnstile data was strangely hard to parse, and oddly frustrating. This code therefore, should be viewed with caution. Please do report any bugs you find!

"""

def foo(x,audit_type):
    """
    filters out non-REGULAR samples
    """
    return [x for x,a in zip(x,audit_type) if a == "REGULAR"]

def bar(d):
    """
    converts the date bits stored in the text file into ms since the epoch
    """
    return int(datetime.datetime(d[2]+2000, d[0], d[1], d[3], d[4], d[5]).strftime("%s"))*1000

def process_line(line):
    """
    processes a single line of the text file
    """
    data = {}
    audit_type = line[3:][2::5]        
    counts = foo(line[3:][3::5], audit_type)
    counts = [int(c) for c in counts]
    times = foo(line[3:][1::5], audit_type)
    dates = foo(line[3:][0::5], audit_type)
    date_bits = [d.split("-") + t.split(":") for d,t in zip(dates,times)]
    timestamps = [bar([int(di) for di in d]) for d in date_bits]
    for t,c in zip(timestamps, counts):
        data[t] = c
    return data

# these are the locations that correspond to times square and grand central
ts_locns =  ['R145', 'A021','R143','R151','R148','R147']
gc_locns =  ['R236', 'R238','R237','R240','R237B','R241A']

# first we parse the file into some dictionaries
ts_data = {}
gc_data = {}

with open('turnstile_120211.txt') as fh:
    for line in fh:
        line = line.strip().split(',')
        locn = line[0]
        key = '_'.join(line[:3])
        if locn in ts_locns:
            try:
                ts_data[key].update(process_line(line))
            except KeyError:
                ts_data[key] = process_line(line)
        if locn in gc_locns:
            try:
                gc_data[key].update(process_line(line))
            except KeyError:
                gc_data[key] = process_line(line)

# then we go through and extract the times and the counts, discarding points
# that are equal to zero, and are not of a specific length
times_square = {}
ts_times = set()
for key in ts_data:
    d = ts_data[key]
    if len(d) != 42:
        continue
    times_square[key] = [{"time":t, "count":c} for t,c in d.items() if c != 0]
    for ai in times_square[key]:
        ts_times.add(ai['time'])
ts_times = list(ts_times)
ts_times.sort()
ts_columns = []
for i in range(len(times_square)):
    ts_columns.append("ts_%s"%i)

grand_central = {}
gc_times = set()
for key in gc_data:
    d = gc_data[key]
    if len(d) != 43:
        continue
    grand_central[key] = [{"time":t, "count":c} for t,c in d.items() if c != 0]
    for ai in grand_central[key]:
        gc_times.add(ai['time'])
gc_times = list(gc_times)
gc_times.sort()   
gc_columns = []
for i in range(len(grand_central)):
    gc_columns.append("gc_%s"%i)

# build some data frames
ts_df = pandas.DataFrame(index=ts_times, columns=ts_columns)
gc_df = pandas.DataFrame(index=gc_times, columns=gc_columns)

for i,k in enumerate(times_square):
    for ai in times_square[k]:
        ts_df["ts_%s"%i][ai['time']] = ai['count']

for i,k in enumerate(grand_central):
    for ai in grand_central[k]:
        gc_df["gc_%s"%i][ai['time']] = ai['count']

# take the differences between the cumulative counts
ts_df = ts_df.diff()
gc_df = gc_df.diff()

# find their mean
ts = ts_df.mean(1)
gc = gc_df.mean(1)

# kick out any null rows
ts = ts[pandas.notnull(ts)]
gc = gc[pandas.notnull(gc)]

# dump the json
json.dump(
    {
        "times_square": [{"time":t, "count":c} for t,c in zip(ts.index, ts)], 
        "grand_central": [{"time":t, "count":c} for t,c in zip(gc.index, gc)]
    },
    open('../viz/data/turnstile_traffic.json','w')
)


