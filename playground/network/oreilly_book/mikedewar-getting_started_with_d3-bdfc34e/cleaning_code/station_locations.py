import pandas
import json
df = pandas.read_csv('StationEntrances.txt')
df['Latitude'] = df['Latitude'] / 1000000.0
df['Longitude'] = df['Longitude'] / 1000000.0

json.dump(
    [{"lat": lat, "lon": lon, "ada": ada} for lat, lon, ada in zip(df['Latitude'], df['Longitude'], df['ADA'])],    
    open("../viz/data/station_entrances.json",'w')
)