import tkinter as tk
import webbrowser
import folium
from skyfield.api import Topos, load, EarthSatellite
from skyfield.timelib import Time
import requests
from datetime import datetime
from math import *
import numpy as np
from shapely.geometry import MultiPoint

# Function to calculate distance using haversine formula
def haversine(lon1, lat1, lon2, lat2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert degrees to radians
    lon1_rad = radians(lon1)
    lat1_rad = radians(lat1)
    lon2_rad = radians(lon2)
    lat2_rad = radians(lat2)

    # Differences in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula - https://en.wikipedia.org/wiki/Haversine_formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return distance
    
# Function to calculate the distance between two points on Earth
def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Earth's radius in kilometers
    earth_radius = 6371.0

    # Calculate the difference between the latitudes and longitudes
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Use the Haversine formula to calculate the distance between two points
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = earth_radius * c

    return distance

# Function to fetch TLE data from the given link
def fetch_tle_data(url):
    tle_data = []
    response = requests.get(url)
    if response.status_code == 200:
        tle_lines = response.text.splitlines()
        for i in range(0, len(tle_lines), 3):
            name = tle_lines[i].strip()
            line1 = tle_lines[i + 1].strip()
            line2 = tle_lines[i + 2].strip()
            tle_data.append((name, line1, line2))
    return tle_data

# Function to calculate RMS error
def calculate_rms(predicted, observed):
    return np.sqrt(np.mean((np.array(predicted) - np.array(observed))**2))

# Function to calculate satellite positions and RMS
def calculate_positions_and_rms(tle_data):
    ts = load.timescale()
    t = ts.now()
    satellite_data = []

    # Calculate positions and RMS for each satellite
    for name, line1, line2 in tle_data:
        satellite = EarthSatellite(line1, line2, name, ts)

        # Get the geocentric position
        geocentric = satellite.at(t)
        subpoint = geocentric.subpoint()

        # Dummy observed alt and az for RMS calculation
        # In practice, replace these with actual observed values
        observed_alt_az = [30, 40]
        predicted_alt_az = [subpoint.latitude.degrees, subpoint.longitude.degrees]

        # Calculate RMS and append to the list
        rms = calculate_rms(predicted_alt_az, observed_alt_az)

        # Add satellite details to the list
        satellite_data.append({
            "OBJECT_NAME": name, 
            "LATITUDE": subpoint.latitude.degrees, 
            "LONGITUDE": subpoint.longitude.degrees, 
            "RMS": rms
        })

    return satellite_data

# Function to filter satellites within a certain radius
def filter_satellites_within_radius(satellite_data, input_lat, input_lon, input_radius):
    filtered_satellites = []

    for sat in satellite_data:
        sat_lat = sat["LATITUDE"]
        sat_lon = sat["LONGITUDE"]
        
        # Calculate the distance between the satellite and the input location
        distance = haversine(input_lon, input_lat, sat_lon, sat_lat)

        # If the distance is less than the input radius, add the satellite to the filtered list
        if distance <= input_radius:
            filtered_satellites.append(sat)

    return filtered_satellites


# Function to show the satellites and the ideal point on a map
def show_map(satellites, input_lat, input_lon, input_radius):
    # Check if the list is empty
    if not satellites:
        print("No satellites found within the specified radius.")
        return

    # Extract latitude and longitude for all the satellites
    satellite_latitudes = [sat["LATITUDE"] for sat in satellites]
    satellite_longitudes = [sat["LONGITUDE"] for sat in satellites]

    # Calculate the centroid of satellite positions
    centroid_lat = sum(satellite_latitudes) / len(satellite_latitudes)
    centroid_lon = sum(satellite_longitudes) / len(satellite_longitudes)

    # Create a map centered at the user-specified location
    map_center = [input_lat, input_lon]
    m = folium.Map(location=map_center, zoom_start=6)

    # Create a FeatureGroup for satellite markers
    satellites_group = folium.FeatureGroup(name='Satellites')

    # Add a marker for each satellite to the satellites group
    for sat in satellites:
        # Extract satellite details
        sat_name = sat['OBJECT_NAME']
        sat_rms = sat['RMS']
        sat_lat = sat['LATITUDE']
        sat_lon = sat['LONGITUDE']

        # The popup text includes the satellite name, RMS, and specific location
        popup_text = f"Satellite: {sat_name}<br>RMS: {sat_rms:.2f}<br>Location: {sat_lat:.6f}, {sat_lon:.6f}"
        folium.Marker([sat_lat, sat_lon], popup=popup_text).add_to(satellites_group)

    # Add the satellites group to the map
    satellites_group.add_to(m)
    folium.Circle(location=map_center, radius=input_radius * 1000, color='blue', fill=False).add_to(m)

    # Add a red marker for the centroid (most ideal point)
    folium.Marker([centroid_lat, centroid_lon], popup="Ideal Point", icon=folium.Icon(color='red')).add_to(m)

    m.save("map.html")
    webbrowser.open("map.html")

# Function to handle the TLE data URL input and display drones on the map
def on_submit():
    # Get the input point coordinates
    lat = float(lat_entry.get())
    lon = float(lon_entry.get())

    # Get the radius input
    radius = float(radius_entry.get())

    # Fetch TLE data from the given URL
    tle_data = fetch_tle_data("https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")

    # Calculate satellite positions and RMS
    satellite_data = calculate_positions_and_rms(tle_data)

    # Filter satellites within the specified radius
    filtered_satellites = filter_satellites_within_radius(satellite_data, lat, lon, radius)

    # Display the filtered satellites on a map
    show_map(filtered_satellites, lat, lon, radius)


# Create the GUI window
window = tk.Tk()
window.title("Choose random point")
window.geometry("400x200")

# Latitude input
lat_label = tk.Label(window, text="Latitude:")
lat_label.pack()
lat_entry = tk.Entry(window)
lat_entry.pack()

# Longitude input
lon_label = tk.Label(window, text="Longitude:")
lon_label.pack()
lon_entry = tk.Entry(window)
lon_entry.pack()

# Radius input
radius_label = tk.Label(window, text="Radius (km):")
radius_label.pack()
radius_entry = tk.Entry(window)
radius_entry.pack()

# Submit button
submit_button = tk.Button(window, text="Submit", command=on_submit)
submit_button.pack()

# Run the GUI event loop
window.mainloop()
