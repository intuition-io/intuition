import json
import csv
import numpy as np

def time_delta(date1,date2):
    """
    we have to write a tiny little script to calcualte time differences
    it's assumed that date1 is later than date2
    """
    f = lambda d: map(int,d.split(":"))
    h,m,s = (d[0] - d[1] for d in zip(f(date1), f(date2)))
    return h*60*60 + m*60 + s
    
with open('trips.txt') as fh:
    """
    route_id,service_id,trip_id,trip_headsign,direction_id,block_id,shape_id
    """
    reader = csv.reader(fh)
    reader.next()
    trip_id_2_route_id = {}
    for line in reader:
        trip_id_2_route_id[line[2]] = line[0]
       
route_ids = ["C", "G", "1", "F", "L"]

out = dict([(route_id, []) for route_id in route_ids])


with open('stop_times.txt') as fh:
    """
    trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign,pickup_type,drop_off_type,shape_dist_traveled
    """
    reader = csv.reader(fh)
    reader.next() 
    stop_times = dict([(rid,{}) for rid in route_ids])
    for line in reader:
        route_id = trip_id_2_route_id[line[0]]
        stop_id = line[3]
        if route_id in stop_times:
            h,m,s = tuple(map(int,line[1].split(":")))
            times = stop_times[route_id].get(stop_id,[])
            times.append(h*60*60 + m*60 + s)
            stop_times[route_id][stop_id] = times
    
out = {}
for route_id, stops in stop_times.items():
    out[route_id] = []
    for stop, times in stops.items():
        deltas = np.diff(np.array(times))
        deltas = [d/60. for d in deltas if d > 0]
        out[route_id].extend(deltas)

out = [
    {
        "route_id": route_id,
        "interarrival_times": times
    }
    for route_id, times in out.items()
]

json.dump(out, open('../viz/data/interarrival_times.json','w'), indent=True)