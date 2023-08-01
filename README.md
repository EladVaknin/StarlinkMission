# Starlink Project
![image](https://github.com/EladVaknin/StarlinkMission/assets/74238558/5b9cc6ce-a7e8-4b7c-b6a3-0ca30534fc9f)



## Overview

This project represents a simulation of GPS using the Starlink Seattle system. It utilizes TLE (Two-Line Element) data for Starlink satellites and calculates their positions to simulate a GPS-like functionality. The program allows users to input their location (latitude, longitude) and a desired radius, and then filters and displays Starlink satellites within that radius on a map using Tkinter, Folium, and Skyfield libraries.

## What is Starlink?

Starlink is a satellite internet constellation project developed by SpaceX, the private space exploration company founded by Elon Musk. The project aims to provide global broadband internet coverage by deploying a large network of small satellites in low Earth orbit (LEO). These satellites work together to create a mesh network, enabling internet connectivity even in remote and underserved areas around the world.

## Benefits of using Starlink over GPS system

While Starlink is primarily designed to provide global internet access, its satellite constellation can also offer potential benefits for location-based services similar to GPS. Here are some advantages of using Starlink for location services over traditional GPS:

1. Global Coverage: Starlink's satellite constellation provides global coverage, including remote and rural regions where traditional GPS signals may be weak or unavailable.

2. Low Latency: Starlink's LEO satellites can offer low-latency connections, potentially leading to faster and more accurate location updates.

3. Redundancy: The large number of satellites in the Starlink constellation offers redundancy, reducing the risk of service disruption due to individual satellite failures.

4. Upgradability: As Starlink continues to expand and upgrade its satellite network, the location accuracy and coverage could potentially improve over time.

5. Integration with Internet Services: Utilizing Starlink for location services can be advantageous for applications that require both location data and internet connectivity, as it offers both functionalities from a single system.

## How to use the code
- Please read the notes below.
1. Install the required libraries:
   - tkinter
   - webbrowser
   - folium
   - skyfield
   - requests
   - numpy
   - shapely
   - (you can download requirements.txt file and run pip install -r requirements.txt)
2. Run the Python script: Execute the code in a Python environment that has the required libraries installed.

3. Input Location and Radius: When the GUI window appears, enter your desired location's latitude and longitude and specify the radius (in kilometers) within which you want to find Starlink satellites.
![image](https://github.com/EladVaknin/StarlinkMission/assets/74238558/caf57e48-1c71-462c-b27f-7750ba2b0e85)

4. Click the "Submit" button: After entering the location and radius, click the "Submit" button. The program will fetch TLE data for Starlink satellites, calculate their positions, and display the satellites within the specified radius on a map.

5. View the Map: A web browser will automatically open with a map showing the filtered Starlink satellites as markers. Click on a marker to see the satellite's name and its RMS (Root Mean Square) error, which provides an estimate of the satellite's position accuracy.
![image](https://github.com/EladVaknin/StarlinkMission/assets/74238558/4a34b115-5910-45c6-aeb0-d323ba44a0ec)








# Feature 2 - Ideal Transmitter Point:
In this feature, the application receives a random point in the radius and now displays the most ideal point, this point represents the most suitable location to place a transmitter for optimal satellite communication.

Showing the ideal point
The ideal point is marked on the map in red. The red marker popup indicates that it represents the "ideal point". This point is calculated as the center of all satellite locations within the specified radius.
This is the best point in the radius to put the transmitter.
Placing a transmitter in this location will provide signal quality and reduce communication interference.

### Instructions
1. Run ideal.py script.
2. Input random location an radius 
![image](https://github.com/EladVaknin/StarlinkMission/assets/74238558/8bdfa533-f0c1-454f-9bbc-c5452c6f2908)
4. You got the ideal point in the radius to put the transmitter:
![image](https://github.com/EladVaknin/StarlinkMission/assets/74238558/02e6048f-4ce1-4f4f-b49e-aaf654f46d0b)

# Feature 3  - Navigation by RMS :
In this feature we will define the starting point in the code (line 213).
And choose a random point and radius as mentioned above - which is the target point.
This simulation will try to create the best route between the two points according to the RMS data, until reaching the selected point.
The route is marked with a red line.
1. make sure that the choosed points in the radius.
1. run navigation.py
2. ![image](https://github.com/EladVaknin/StarlinkMission/assets/74238558/511b99ac-14e4-4172-8531-5820856e206f)









#

Notes:
*  This link https://celestrak.org/NORAD/elements/starlink.txt issues the information and is limited in its readability.
In case it doesn't respond please use the starlink.txt file.

 * The simulated GPS functionality in this project is based on the positions of Starlink satellites at the current datetime and uses dummy observed altitude and azimuth values for RMS calculations.

 **Instructed by Professor Boaz Ben Moshe.**



## Important Links

- [Starlink Official Website](https://www.starlink.com/)
- [Skyfield Library Documentation](https://rhodesmill.org/skyfield/)
- https://celestrak.org/NORAD/elements/
