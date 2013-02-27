import csv
import numpy as np
import json
import scipy.spatial

with open('stops.txt') as fh:
    reader = csv.reader(fh)
    lats = []
    lons = []
    names = []
    for line in reader:
        if 'Times' in line[2]:
            lats.append(float(line[4]))
            lons.append(float(line[5]))
            names.append(line[0])

positions = np.vstack([lats,lons]).T

D = scipy.spatial.distance_matrix(positions, positions)

out = {
    "matrix": [list(row) for row in D],
    "names": names
}

json.dump(out, open('../viz/data/station_distances.json','w'))