import requests
from bs4 import BeautifulSoup
import pandas as pd

def grab_riders_initial():
    # URL of the website to scrape
    url = "https://racerxonline.com/sx/riders"

    # Send a GET request to the website
    response = requests.get(url)

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
        df.to_csv('supercross-statistics.csv', index=False)
        print("Data saved to riders.csv")
    else:
        print(f"Failed to retrieve information from the webpage. Status code: {response.status_code}")

def grab_riders_update():
    # Just putting some stuff here
    return