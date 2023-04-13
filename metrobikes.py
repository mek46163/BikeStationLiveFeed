# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 12:55:18 2022

@author: Korbinian Meier
"""





from urllib.request import urlopen
from urllib.request import Request

from os.path import exists

from geopy import distance
import datetime
import json
import folium

import osmnx as ox
import networkx as nx
import jinja2 as j2

class LatLngPopup(folium.MacroElement):
    """
    When one clicks on a Map that contains a LatLngPopup,
    a popup is shown that displays the latitude and longitude of the pointer.

    """
    _template = j2.Template(u"""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                data = e.latlng.lat.toFixed(4) + "," + e.latlng.lng.toFixed(4);
                    {{this.get_name()}}
                        .setLatLng(e.latlng)
                        .setContent( "<br /><p>Latitude: "+ e.latlng.lat.toFixed(4) + "</p><p>Longitude: "+ e.latlng.lng.toFixed(4) + "</p><button onclick= parent.setSource('"+ e.latlng.lat.toFixed(4) + ","+ e.latlng.lng.toFixed(4) + "')>Set as Source</button><br /><button onclick=parent.setDest('"+ e.latlng.lat.toFixed(4) + ","+ e.latlng.lng.toFixed(4) + "')>Set as Destination</button>")
                        .openOn({{this._parent.get_name()}})
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);

            {% endmacro %}
            """)  # noqa

    def __init__(self):
        super(LatLngPopup, self).__init__()
        self._name = 'LatLngPopup'


print("loading...")
central_location = [34.0427, -118.2477]

if exists("graph_bike.graphml"):
    graph_bike = ox.load_graphml("graph_bike.graphml")
else:
    graph_bike=ox.graph_from_place('Los Angeles, California', network_type='walk')
    ox.save_graphml(graph_bike, filepath="graph_bike.graphml")

#graph_bike=ox.graph_from_place('Los Angeles, California', network_type='walk')
print("finished loading")   
def load_data():
    with open("stations.json", "r") as stations_file:
        metro_bike_json = json.loads(stations_file.read())
        file_date = datetime.datetime.fromtimestamp(metro_bike_json['date'])
        file_age_in_minutes = ((datetime.datetime.now()-file_date).total_seconds()/60)
        print(file_age_in_minutes)
        if file_age_in_minutes>10:
            req = Request("https://bikeshare.metro.net/stations/json/", headers={'User-Agent': 'Mozilla/5.0'})
            remotefile = urlopen(req).read()
            metro_bike_json = json.loads(remotefile)
            metro_bike_json['date'] = datetime.datetime.now().timestamp()
            
            with open("stations.json", "w") as outfile:
                json.dump(metro_bike_json, outfile)
    

    return metro_bike_json
    

def sort_by_distance(stations, lat, long):
    #Note: Latitude and Longitude are exchanged in GeoJson
    for coords in stations['features']:
        lat_dest = coords['geometry']['coordinates'][1]
        long_dest = coords['geometry']['coordinates'][0]
        dist = distance.geodesic((lat_dest, long_dest), (lat, long)).km
        long_dest = coords['distance'] = dist

    features = stations['features']
    data = sorted(features, key=lambda d: d['distance'])
    return data



def get_stations_bikes_avail(lat, long, n): 

    metro_bike_json = load_data()
    data = sort_by_distance(metro_bike_json, lat, long)
   
    result = {}
    i = 0
    j = 0
    while j<n and i < len(data):
        if data[i]['properties']['bikesAvailable'] > 0:
            result[j] = data[i]
            j += 1
        i +=1    
    res = json.dumps(result, indent=2, sort_keys=True)

    
    #return new_data
    return res

def new_map(curr_loc):
    
    my_map = folium.Map(location=curr_loc, zoom_start=14)
    ic = folium.map.Icon(icon="location-crosshairs", prefix="fa-solid fa-location", color="black")
    folium.Marker(location=curr_loc, icon=ic).add_to(my_map)
    m = LatLngPopup()
    m.add_to(my_map)
    
    return my_map

def get_stations_docks_avail(lat, long, n):
    metro_bike_json = load_data()
    data = sort_by_distance(metro_bike_json, lat, long)
    
    result = {}
    i = 0
    j = 0
    while j<n and i < len(data):
        if data[i]['properties']['docksAvailable'] > 0:
            result[j] = data[i]
            j += 1
        i +=1    
    res = json.dumps(result, indent=2, sort_keys=True)
    return res

def show_on_map(coords, curr_loc):
    my_map = new_map(curr_loc)
    entries = json.loads(coords)
#    print(entries['0']['geometry']['coordinates'])
    for entry in entries:
        #print(entries[entry]['geometry']['coordinates'])
        coord_marker = [entries[entry]['geometry']['coordinates'][1], entries[entry]['geometry']['coordinates'][0]]
        name = entries[entry]['properties']['name']
        street = entries[entry]['properties']['addressStreet']
        city = entries[entry]['properties']['addressCity']
        html = "<p>Name: " + name + "</p><p>Address: " + street + ","+city
        popup = folium.Popup(html=html)
        folium.Marker(location=coord_marker, popup=popup).add_to(my_map)
        
    my_map.save("map.html")
    return my_map

def draw_route(source_loc, dest_loc, my_map, graph):
   #folium.Marker(location=source_loc).add_to(my_map)
   # folium.Marker(location=dest_loc).add_to(my_map)
    #graph_bike = ox.graph_from_point(current_location, network_type='walk', dist=1000)
    print(float(source_loc[1]))
    print(float(dest_loc[1]))
    source = ox.nearest_nodes(graph, float(source_loc[1]), float(source_loc[0]))
    dest = ox.nearest_nodes(graph, float(dest_loc[1]), float(dest_loc[0]))
    route1 = nx.shortest_path(graph, source, dest, weight="length")
    print(len(route1))
    if(len(route1) > 1):
        ox.plot_route_folium(graph, route1, route_map=my_map)
    my_map.save("map.html")
    return my_map

def route_using_metrobike(source_loc, dest_loc):
    #get station where you get the bike for the route
    nearest_bikes = json.loads(get_stations_bikes_avail(source_loc[0], source_loc[1], 1))
    nearest_bikes_coord = [nearest_bikes['0']['geometry']['coordinates'][1], nearest_bikes['0']['geometry']['coordinates'][0]]
    my_map = new_map(source_loc)
    #add marker and popup for the station, where you get the bike
    name = nearest_bikes['0']['properties']['name']
    street = nearest_bikes['0']['properties']['addressStreet']
    city = nearest_bikes['0']['properties']['addressCity']
    html = "<p>Name: " + name + "</p><p>Address: " + street + ","+city
    popup = folium.Popup(html=html)
    
    ico = folium.Icon(color="green")
    folium.Marker(location = nearest_bikes_coord, icon=ico, popup=popup).add_to(my_map)
    
    #get station where you can give back your bike
    nearest_docks = json.loads(get_stations_docks_avail(dest_loc[0], dest_loc[1], 1))
    nearest_docks_coord = [nearest_docks['0']['geometry']['coordinates'][1], nearest_docks['0']['geometry']['coordinates'][0]]
    #add marker and popup for the station where you give back your bike
    name = nearest_docks['0']['properties']['name']
    street = nearest_docks['0']['properties']['addressStreet']
    city = nearest_docks['0']['properties']['addressCity']
    html = "<p>Name: " + name + "</p><p>Address: " + street + ","+city
    popup = folium.Popup(html=html)
    
    ico2 = folium.Icon(color="red")
    folium.Marker(location=nearest_docks_coord, icon=ico2, popup=popup).add_to(my_map)
    
    ico3 = folium.Icon(color="blue")
    folium.Marker(location=dest_loc, icon=ico3).add_to(my_map)
    source_loc[0] = float(source_loc[0])
    source_loc[1] = float(source_loc[1])
    print(source_loc[1])

    
    my_map = draw_route(source_loc, nearest_bikes_coord, my_map, graph_bike)
    my_map = draw_route(nearest_bikes_coord, nearest_docks_coord, my_map, graph_bike)
    my_map = draw_route(nearest_docks_coord, dest_loc, my_map, graph_bike)
    return my_map

# my_map = folium.Map(location=current_location, zoom_start=20)
# ic = folium.map.Icon(icon="location-crosshairs", prefix="fa-solid fa-location", color="black")
# folium.Marker(location=current_location, icon=ic).add_to(my_map)


# processed_data = get_stations_bikes_avail(current_location[0], current_location[1], 5)
# processed_data2 = get_stations_docks_avail(current_location[0], current_location[1], 5)
# show_on_map(processed_data, current_location)
# show_on_map(processed_data2, current_location)
loc = [34.018901, -118.248131]
#test = get_stations_bikes_avail(current_location[0], current_location[1], 1)        
#route_using_metrobike(current_location, loc)
