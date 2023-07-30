import tkinter as tk
import webbrowser
import folium
import os
import numpy as np
import requests
from datetime import datetime
from skyfield.api import Topos, load, EarthSatellite, utc
from pytz import timezone

# Load TLE data from the Celestrak API
def get_tle_data():
    url = "https://www.celestrak.com/NORAD/elements/starlink.txt"
    response = requests.get(url)
    tle_data = response.text.strip()  # Remove leading/trailing whitespaces and newline characters
    tle_sets = tle_data.split('\r\n')  # Split the data into individual TLE sets
    return tle_sets

# Calculate positions and RMS values for all satellites in the TLE data at a specific time and location
def calculate_positions_and_rms(tle_sets, lat, lon, t):
    satellites = []
    ts = load.timescale()

    for tle_set in tle_sets:
        satellite = EarthSatellite(tle_set[1], tle_set[2], tle_set[0], ts)
        satellites.append(satellite)

    # Convert the input datetime (t) to UTC with timezone information
    eastern = timezone('US/Eastern')  # Adjust this timezone as needed
    t_utc = eastern.localize(t).astimezone(utc)

    positions = [satellite.at(ts.utc(t_utc)).position.km for satellite in satellites]

    # Calculate range vectors from observer to each satellite
    observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
    range_vectors = [(position[0] - observer.longitude.degrees,
                      position[1] - observer.latitude.degrees,
                      position[2]) for position in positions]

    # Calculate the squared range magnitudes
    range_magnitudes_squared = [(rv[0] ** 2 + rv[1] ** 2 + rv[2] ** 2) for rv in range_vectors]

    # Calculate the RMS
    rms = (sum(range_magnitudes_squared) / len(range_magnitudes_squared)) ** 0.5

    return positions, rms

def find_best_position(tle_data, lat_range, lon_range, radius):
    best_rms = float('inf')
    best_lat = 0.0
    best_lon = 0.0

    for lat in np.arange(lat_range[0], lat_range[1], 0.1):
        for lon in np.arange(lon_range[0], lon_range[1], 0.1):
            t = datetime.utcnow()
            print(f"Calculating for latitude {lat}, longitude {lon}...")
            satellite_data = calculate_positions_and_rms(tle_data, lat, lon, t)
            rms_value = satellite_data[1]
            print(f"RMS value for latitude {lat}, longitude {lon}: {rms_value}")
            if rms_value < best_rms:
                best_rms = rms_value
                best_lat = lat
                best_lon = lon

    print(f"Best latitude: {best_lat}, Best longitude: {best_lon}, Best RMS: {best_rms}")
    return best_lat, best_lon, best_rms
# Function to show the satellites near the best position on a map
def show_satellites_near_position(tle_data, best_lat, best_lon, input_radius):
    t = datetime.utcnow()
    satellite_data = calculate_positions_and_rms(tle_data, best_lat, best_lon, t)
    filtered_satellites = filter_satellites_near_position(satellite_data[0], best_lat, best_lon, input_radius)

    if not filtered_satellites:
        print("No satellites found within the specified radius.")
        return

    map_center = [best_lat, best_lon]
    m = folium.Map(location=map_center, zoom_start=6)

    folium.Circle(location=map_center, radius=input_radius * 1000, color='blue', fill=False).add_to(m)

    for sat in filtered_satellites:
        popup_text = f"{sat['OBJECT_NAME']}, RMS: {sat['RMS']:.2f}"
        folium.Marker([sat["LATITUDE"], sat["LONGITUDE"]], popup=popup_text).add_to(m)

    map_filename = "map.html"
    m.save(map_filename)
    webbrowser.open("file://" + os.path.abspath(map_filename))

# Filter satellites that are within a certain radius from the specified position
def filter_satellites_near_position(satellite_data, lat, lon, radius):
    filtered_satellites = []
    for i in range(len(satellite_data)):
        distance_km = haversine_distance(lat, lon, satellite_data[i][1], satellite_data[i][0])
        if distance_km <= radius:
            filtered_satellites.append({
                "OBJECT_NAME": f"Satellite {i+1}",
                "RMS": satellite_data[i][2],
                "LATITUDE": satellite_data[i][1],
                "LONGITUDE": satellite_data[i][0]
            })
    return filtered_satellites

# Haversine formula to calculate distance between two points on Earth's surface
def haversine_distance(lat1, lon1, lat2, lon2):
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(np.radians, [lat1, lon1, lat2, lon2])
    d_lat = lat2_rad - lat1_rad
    d_lon = lon2_rad - lon1_rad
    a = np.sin(d_lat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(d_lon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of Earth in km
    distance = r * c
    return distance

# Function to handle the "Submit" button click event
def on_submit():
    tle_data = get_tle_data()
    lat_range = [float(input_min_lat.get()), float(input_max_lat.get())]
    lon_range = [float(input_min_lon.get()), float(input_max_lon.get())]
    radius = float(input_radius.get())

    best_lat, best_lon, best_rms = find_best_position(tle_data, lat_range, lon_range, radius)
    show_satellites_near_position(tle_data, best_lat, best_lon, radius)

# Tkinter GUI setup
root = tk.Tk()
root.title("Starlink Satellite Tracker")

tk.Label(root, text="Latitude Range (min, max)").grid(row=0, column=0, padx=5, pady=5)
input_min_lat = tk.Entry(root)
input_min_lat.grid(row=0, column=1, padx=5, pady=5)
input_min_lat.insert(0, "20")

input_max_lat = tk.Entry(root)
input_max_lat.grid(row=0, column=2, padx=5, pady=5)
input_max_lat.insert(0, "40")

tk.Label(root, text="Longitude Range (min, max)").grid(row=1, column=0, padx=5, pady=5)
input_min_lon = tk.Entry(root)
input_min_lon.grid(row=1, column=1, padx=5, pady=5)
input_min_lon.insert(0, "-120")

input_max_lon = tk.Entry(root)
input_max_lon.grid(row=1, column=2, padx=5, pady=5)
input_max_lon.insert(0, "-80")

tk.Label(root, text="Radius (km)").grid(row=2, column=0, padx=5, pady=5)
input_radius = tk.Entry(root)
input_radius.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
input_radius.insert(0, "200")

submit_button = tk.Button(root, text="Submit", command=on_submit)
submit_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
