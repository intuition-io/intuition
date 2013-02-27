import networkx as nx
import json

out = {}

G = nx.Graph()

"""
stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon,zone_id,stop_url,location_type,parent_station
"""
stops = {}
stop_names = {}
with open('stops.txt') as fh:
    fh.next()
    for line in fh:
        d = line.split(',')
        stop_id = d[0]
        parent_id = d[9].strip()
        location_type = int(d[8])
        stop_name = d[2]
        if location_type == 0:
              stops[stop_id] = parent_id
        else:
            stop_names[stop_id] = stop_name


"""
trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign,pickup_type,drop_off_type,shape_dist_traveled
"""
prev_stop_id = None
with open('stop_times.txt') as fh:
    fh.next()
    for line in fh:
        d = line.split(',')
        stop_id = stops.get(d[3], d[3])
        stop_seq = int(d[4])
        if stop_seq != 1:
            G.add_edge(
                stop_names[prev_stop_id], 
                stop_names[stop_id]
            )
        prev_stop_id = stop_id

nodes = G.nodes()

out['nodes'] = [{'name': node} for node in nodes]
out['links'] = [{'source': nodes.index(source), 'target': nodes.index(target)} for source, target in G.edges()]

json.dump(out, open('../viz/data/stations_graph.json','w'))