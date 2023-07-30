import tkinter as tk
import webbrowser
import folium
from skyfield.api import Topos, load, EarthSatellite
from skyfield.timelib import Time
import requests
from datetime import datetime
from math import *
import numpy as np
from folium.vector_layers import PolyLine


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

    # Haversine formula
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

    # Current datetime
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

def simulate_movement(start_lat, start_lon, target_lat, target_lon, satellites):
    current_lat, current_lon = start_lat, start_lon
    path = [[start_lat, start_lon]]  # initialize path with starting point

    while calculate_distance(current_lat, current_lon, target_lat, target_lon) > 0.001: # Stop condition
        min_rms = float('inf')
        best_direction = None

        for dlat in np.linspace(-0.01, 0.01, 5): # Step size and direction
            for dlon in np.linspace(-0.01, 0.01, 5): # Step size and direction
                temp_lat, temp_lon = current_lat + dlat, current_lon + dlon
                
                rms_sum = 0
                for sat in satellites:
                    sat_lat = sat["LATITUDE"]
                    sat_lon = sat["LONGITUDE"]
                    distance = haversine(temp_lon, temp_lat, sat_lon, sat_lat)
                    rms_sum += distance
                
                if len(satellites) > 0:
                    rms = rms_sum / len(satellites)
                else:
                    raise Exception("No satellites found within the specified radius.")

                
                if rms < min_rms:
                    min_rms = rms
                    best_direction = (dlat, dlon)

        # Update current location
        if best_direction:
            current_lat += best_direction[0]
            current_lon += best_direction[1]
            path.append([current_lat, current_lon])

    return current_lat, current_lon, path

def show_map(satellites, input_lat, input_lon, input_radius, path=None):
    # Check if the list is empty
    if not satellites:
        print("No satellites found within the specified radius.")
        return

    # Create a map centered at the user-specified location
    map_center = [input_lat, input_lon]
    m = folium.Map(location=map_center, zoom_start=6)

    # Add a circle to represent the radius
    folium.Circle(location=map_center, radius=input_radius*1000, color='blue', fill=False).add_to(m)

    # Add a marker for each satellite
    for sat in satellites:
        # The popup text includes the satellite name and its RMS
        popup_text = f"{sat['OBJECT_NAME']}, RMS: {sat['RMS']:.2f}"
        folium.Marker([sat["LATITUDE"], sat["LONGITUDE"]], popup=popup_text).add_to(m)

    # Add a line representing the path
    if path:
        PolyLine(path, color="red", weight=2.5, opacity=1).add_to(m)

    # Save the map to an HTML file
    m.save("map.html")

    # Open the HTML file in a web browser
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
    # Perform the simulation
    start_lat, start_lon = 34, 30  # Or wherever you want to start
    final_lat, final_lon, path = simulate_movement(start_lat, start_lon, lat, lon, filtered_satellites)

    print("Final location after simulation:", final_lat, final_lon)
    # Display the filtered satellites on a map
    show_map(filtered_satellites, lat, lon, radius, path)


# Create the GUI window
window = tk.Tk()
window.title("Object Filter")
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
