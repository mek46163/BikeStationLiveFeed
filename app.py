# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 19:15:38 2022

@author: Korbinian Meier
"""
import metrobikes
from flask import Flask,render_template, request

app=Flask(__name__, 
          template_folder="views")

errMessage = "One or more values are missing"
default_map = metrobikes.new_map(metrobikes.central_location)

@app.route('/')
def home():
    map1 = metrobikes.new_map(metrobikes.central_location)
    return render_template("home.html", map1=map1._repr_html_())

@app.route('/bikes', methods=['GET', 'POST'])
def bikes():
    lat = request.args.get('latitude')
    long = request.args.get('longitude')
    curr_loc=[lat, long]

    if lat=="" or long == "" or request.args.get('number') == "":
        return render_template("home.html", errMessage=errMessage, map1=default_map._repr_html_())
    num = int(request.args.get('number'))
    test = metrobikes.get_stations_bikes_avail(lat, long, num)
    bike_map = metrobikes.show_on_map(test, curr_loc)
    return render_template("home.html", map1=bike_map._repr_html_())

@app.route('/docks', methods=['GET', 'POST'])
def docks():
    lat = request.args.get('latitude')
    long = request.args.get('longitude')
    curr_loc=[lat, long]

    if lat=="" or long == "" or request.args.get('number') == "":
        return render_template("home.html", errMessage=errMessage, map1=default_map._repr_html_())
    num = int(request.args.get('number'))
    test = metrobikes.get_stations_docks_avail(lat, long, num)
    dock_map = metrobikes.show_on_map(test, curr_loc)
    return render_template("home.html", map1=dock_map._repr_html_())

@app.route('/route', methods=['GET', 'POST'])
def route():
    source_lat = request.args.get('latitude')
    source_long = request.args.get('longitude')
    curr_loc=[source_lat, source_long]
    dest_lat = request.args.get('dest-latitude')
    dest_long = request.args.get('dest-longitude')
    dest_loc=[dest_lat, dest_long]
    if source_lat == "" or source_long == "" or dest_lat == "" or dest_long == "":
        return render_template("home.html", errMessage=errMessage, map1=default_map._repr_html_())
    route_map = metrobikes.route_using_metrobike(curr_loc, dest_loc)
    return render_template("home.html", map1=route_map._repr_html_())

if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000)