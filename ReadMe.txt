Los Angeles Metrobikes Stations live feed:
by Korbinian Meier

Modules needed:
flask
urllib
os
geopy
datetime
json
folium
osmnx
networkx
jinja2

Instructions:
-Install the modules
-run app.py, it can take up to 3 minutes for the server to be ready, depending on the machine's memory and CPU
-Open a browser(preferably Mozilla Firefox) and go to following address: http://127.0.0.1:5000

-Finding k nearest Metrobikes stations with bikes available:
	-enter source coordinates into the input fields and the number of the stations to be searched(or click on the map at the desired location and press "set as source" in the popup)
	-click on "Get nearest stations with bikes"

-Finding k nearest Metrobikes stations with docks available:
	-enter source coordinates into the input fields and the number of the stations to be searched(or click on the map at the desired location and press "set as source" in the popup)
	-click on "Get nearest stations with docks"

-Show the route between two locations using Los Angeles Metrobikes:
	-enter source coordinates into the input fields(or click on the map at the desired location and press "set as source" in the popup)
	-enter destination coordinates into the input fields for the destination(or click on the map at the desired location and press "set as destination" in the popup)

