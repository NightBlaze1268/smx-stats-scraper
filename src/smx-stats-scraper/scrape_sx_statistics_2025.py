import requests
from bs4 import BeautifulSoup
import pandas as pd
from os import path
from logos import yamaha_logo, honda_logo, kawasaki_logo, ktm_logo, husqvarna_logo, gasgas_logo, triumph_logo

race_year = 2025
rider_url = "https://racerxonline.com/sx/riders"
output_file = "supercross-statistics-2025.csv"
base_track_url = "https://racerxonline.com/sx/2025/{track}/{_class_}"
race_tracks = {
    "anaheim-1": ["450sx", "250sx-west"],
    "san-diego": ["450sx", "250sx-west"],
    "anaheim-2": ["450sx", "250sx-west"],
    "glendale": ["450sx", "250sx-west"],
    "tampa": ["450sx", "250sx-east"],
    "detroit": ["450sx", "250sx-east"],
    "arlington": ["450sx", "250sx-west"],
    "daytona": ["450sx", "250sx-east"],
    "indianapolis": ["450sx", "250sx-showdown"],
    "birmingham": ["450sx", "250sx-east"],
    "seattle": ["450sx", "250sx-west"],
    "foxborough": ["450sx", "250sx-east"],
    "philadelphia": ["450sx", "250sx-showdown"],
    "east-rutherford": ["450sx", "250sx-east"],
    "pittsburg": ["450sx", "250sx-east"],
    "denver": ["450sx", "250sx-west"],
    "salt-lake-city": ["450sx", "250sx-showdown"],
}
bike_manufacturers = {
    "Yamaha": yamaha_logo,
    "Honda": honda_logo,
    "Triumph": triumph_logo,
    "Kawasaki": kawasaki_logo,
    "KTM": ktm_logo,
    "GasGas": gasgas_logo,
    "Husqvarna": husqvarna_logo
}
points_system = {
    1: 25,
    2: 22,
    3: 20,
    4: 18,
    5: 17,
    6: 16,
    7: 15,
    8: 14,
    9: 13,
    10: 12,
    11: 11,
    12: 10,
    13: 9,
    14: 8,
    15: 7,
    16: 6,
    17: 5,
    18: 4,
    19: 3,
    20: 2,
    21: 1,
    22: 0
}

def __grab_riders_initial__():
    # Send a GET request to the website
    response = requests.get(rider_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the container holding the rider names
        rider_container = soup.find('ul', {'class': 'ui_list grid'})
        # Extract all rider names
        riders_data = []
        if rider_container:
            for rider in rider_container.find_all('a', {'class': 'ui_link'}):
                # Remove leading and trailing whitespace
                full_text = rider.text.strip()
                if full_text:  # Ensure the name is not empty
                    partials = full_text.split()
                    name = ' '.join(partials[:2])
                    location = ' '.join(partials[2:])
                    riders_data.append({'Name': name, 'Location': location})

        # Print the rider names
        for obj in riders_data:
            print(f"Rider: {obj}")

        df = pd.DataFrame(riders_data)
        df['ID'] = range(1, len(df) + 1)
        df = df[['ID', 'Name', 'Location']]
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")

        return df
    else:
        print(f"Failed to retrieve information from the webpage. Status code: {response.status_code}")

def fetch_rider_location(name):
    """Fetch the location of a rider from the rider list."""
    response = requests.get(rider_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rider_container = soup.find('ul', {'class': 'ui_list grid'})
        if rider_container:
            for rider in rider_container.find_all('a', {'class': 'ui_link'}):
                full_text = rider.text.strip()
                if full_text:
                    partials = full_text.split()
                    rider_name = ' '.join(partials[:2])
                    if rider_name == name:
                        return ' '.join(partials[2:])  # Return the location
    return ""  # Return an empty string if the rider is not found

def update_season_data():
    if path.exists(output_file):
        df = pd.read_csv(output_file)
    else:
        df = __grab_riders_initial__()

    df["Points Standings"] = 0

    # Initialize all race columns with 'N/A' for existing riders
    for track in race_tracks.keys():
        if track not in df.columns:
            df[track] = 'N/A'

    # Add columns for bike brand and points standings
    if 'Bike Brand' not in df.columns:
        df['Bike Brand'] = 'N/A'
    if 'Points Standings' not in df.columns:
        df['Points Standings'] = 0


    for track, classes in race_tracks.items():
        for _class_ in classes:
            url = base_track_url.format(track=track, _class_=_class_)
            print(f"Scraping data from: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                track_container = soup.find('table', {'class': 'ui_table zebra mod_mobile'})

                if track_container:
                    # Iterate through each row
                    for i, row in enumerate(track_container.find_all('tr')):
                        name_cell = row.find('a', {'class': 'block'})
                        bike_cell = row.find('a', {'class': 'block', 'href': lambda x: x and '/brand/' in x})
                        if name_cell:
                            name = name_cell.text.strip()
                            position = i  # Position is the index

                            # Fetch bike brand
                            bike_brand = 'N/A'
                            if bike_cell:
                                bike_text = bike_cell.text.strip()
                                for brand in bike_manufacturers.keys():
                                    if brand.lower() in bike_text.lower():
                                        bike_brand = brand
                                        break

                            # Update the DataFrame
                            if name in df['Name'].values:
                                # Only update the specific race column and other non-race columns
                                df.loc[df['Name'] == name, track] = position
                                df.loc[df['Name'] == name, "Class"] = _class_
                                df.loc[df['Name'] == name, "Bike Brand"] = bike_brand
                                if position in points_system:
                                    df.loc[df['Name'] == name, "Points Standings"] += points_system[position]
                            else:
                                # Fetch the rider's location
                                location = fetch_rider_location(name)
                                # Assign a new ID
                                new_id = df['ID'].max() + 1 if not df.empty else 1
                                # Add a new row for the rider
                                new_row = {
                                    'ID': new_id,
                                    'Name': name,
                                    'Location': location,
                                    'Class': _class_,
                                    'Bike Brand': bike_brand,
                                    'Points Standings': points_system.get(position, 0),
                                    **{t: 'N/A' for t in race_tracks.keys()},  # Initialize all races as 'N/A'
                                    track: position  # Update the current race
                                }
                                # Use pd.concat() instead of append
                                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)


    # Save the updated DataFrame
    df.to_csv(output_file, index=False, na_rep="N/A")
    print("Data updated in supercross-statistics-2025.csv")
