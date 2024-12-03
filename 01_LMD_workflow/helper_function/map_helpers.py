import polyline
import folium
import folium.plugins as plugins
import pandas as pd
import requests

def get_map_by_vehicle(curr_route_df):
    
    
    curr_lat_lon_coords = curr_route_df[["Latitude","Longitude"]].values.tolist()
    m = get_map(curr_lat_lon_coords)
    
    return m



def get_map(my_lat_longs):
    m = folium.Map(location=my_lat_longs[1],
                   zoom_start=12)
    count = 0 
    
    for src_idx in range(len(my_lat_longs))[:-1]:
        dst_idx = src_idx + 1
        
        source = my_lat_longs[src_idx]
        destination = my_lat_longs[dst_idx]
        
        route = get_route(source[1], source[0], destination[1], destination[0])
        
        folium.PolyLine(
                route['route'],
                weight=5,
                color='blue',
                opacity=0.6
            ).add_to(m)
        
        if src_idx == 0:
            folium.Marker(
                location=[my_lat_longs[src_idx][0],my_lat_longs[src_idx][1]],
                icon=folium.Icon(color="green",icon="fa-building", prefix='fa')
            ).add_to(m)
            
        else:
            """
            folium.Marker(
                location=route['start_point'],
                icon=folium.Icon(color="blue",icon="fa-map-pin", prefix='fa')
            ).add_to(m)
            """
            folium.Marker(
                location=[my_lat_longs[src_idx][0],my_lat_longs[src_idx][1]],
                icon=plugins.BeautifyIcon(
                         icon="arrow-down", icon_shape="marker",
                         number=src_idx,
                         border_color= 'red',
                     )
            ).add_to(m)

    return m

def get_route(source_long, source_lat, dest_long, dest_lat):
    loc = "{},{};{},{}".format(source_long, source_lat, dest_long, dest_lat)
    url = "http://router.project-osrm.org/route/v1/driving/"
    r = requests.get(url + loc) 

    res = r.json()   
    routes = polyline.decode(res['routes'][0]['geometry'])
    start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
    end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
    distance = res['routes'][0]['distance']
    
    out = {'route':routes,
        'start_point':start_point,
        'end_point':end_point,
        'distance':distance
    }
    
    return out
