import folium
import pandas as pd
import numpy as np
import requests
import polyline

def plot_order_locations(df, location_coordinates, pdp=1):
    # Set up the colours based on well's purpose
    purpose_colour = {'DEPOT':'red', 'Restaurant':'green', 'Retailer':'blue', 'Business': 'orange'}
    if pdp==0:
        purpose_colour = {'DEPOT':'red', 'Pickup':'green', 'Delivery':'blue'}

    map = folium.Map(location=[location_coordinates.lat.mean(), location_coordinates.lng.mean()], 
                     zoom_start=10, control_scale=True)

    #Loop through each row in the dataframe
    for i,row in df.iterrows():
        #Setup the content of the popup
        iframe = folium.IFrame(f'Order ID: {str(row["order_ID"])} \n Order Weight: {str(row["order_wt"])} lbs \n Service time: {str(row["service_time"])} mins')

        #Initialise the popup using the iframe
        popup = folium.Popup(iframe, min_width=200, max_width=200)

        try:
            icon_color = purpose_colour[row['order_type']]
        except:
            #Catch nans
            icon_color = 'gray'

        #Add each row to the map
        folium.Marker(location=[location_coordinates['lat'][i],location_coordinates['lng'][i]],
                      popup = popup, 
                      icon=folium.Icon(color=icon_color, icon='')).add_to(map)


    return map

def get_map_by_vehicle(curr_route_df):
    
    
    curr_lat_lon_coords = curr_route_df[["lat","lng"]].values.tolist()
    location_type = curr_route_df[['order_type']].to_dict()
    m = get_map(curr_lat_lon_coords, location_type)
    
    return m

def get_map(my_lat_longs, location_type):
    m = folium.Map(location=my_lat_longs[1],
                   zoom_start=12)
    count = 0 
    
    purpose_colour = {'DEPOT':'red', 'Pickup':'green', 'Delivery':'blue'}
    
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
                icon=folium.Icon(color="red", prefix='fa')
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
                icon=folium.Icon(color=purpose_colour[location_type['order_type'][src_idx]], prefix='fa')
                # icon=plugins.BeautifyIcon(
                #          #icon="arrow-down", 
                #          icon_shape="marker",
                #          #number=src_idx,
                #          color= purpose_colour[location_type['order_type'][src_id]],
                #      )
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