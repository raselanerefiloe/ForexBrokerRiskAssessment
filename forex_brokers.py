from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

# Create a session
session = requests.Session()

# URLs
homepage_url = "https://www.allfxbrokers.com"
url = "https://www.allfxbrokers.com/forex-brokers"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.allfxbrokers.com/forex-brokers',
    'Connection': 'keep-alive',
}


# Function to fetch the initial broker data
def fetch_broker_list(url, session):
    """Fetch the list of brokers from the forex brokers page."""
    for attempt in range(5):  # Retry up to 5 times
        response = session.get(url, headers=headers)

        if response.status_code == 202:
            print("Request is still processing. Waiting before retrying...")
            time.sleep(20)  # Wait for 5 seconds before retrying
            continue  # Retry the request

        if response.status_code != 200:
            print(f"Failed to retrieve data, status code: {response.status_code}")
            exit()

        return response  # Return the successful response

    print("Max retries reached. Exiting...")
    exit()

# Request the homepage to establish a session
session.get(homepage_url, headers=headers)

# Fetch the broker list
response = fetch_broker_list(url, session)

# Parse the HTML
soup = BeautifulSoup(response.text, 'html.parser')


import re
def fetch_rating_and_regulation_info(link, session):
    """Fetch both rating and regulation information from the broker's individual page."""
    try:
        # Attempt to fetch the page
        for attempt in range(3):  # Retry up to 3 times
            response = session.get(link, headers=headers)

            # If 403 error, handle it
            if response.status_code == 403:
                print(f"Access forbidden for {link}.")
                return '403 Forbidden', 'N/A'

            # Handle 202 processing status
            if response.status_code == 202:
                print(f"Request for {link} is still processing. Waiting before retrying...")
                time.sleep(5)  # Wait for 5 seconds before retrying
                continue  # Retry the request

            if response.status_code != 200:
                print(f"Failed to retrieve data for {link}, status code: {response.status_code}")
                return 'N/A', 'N/A'  # If the request fails, return 'N/A'

            # Parse the broker's page
            broker_soup = BeautifulSoup(response.text, 'html.parser')

            # Fetch Rating Information
            rating_value = '0'  # Default value
            rating_div = broker_soup.find('div', class_='_sum_rating')
            if rating_div:
                rating_span = rating_div.find('span', itemprop='ratingValue')
                if rating_span:
                    rating_value = float(rating_span.text.strip())  # Extract the rating as a float
                    print(f"Rating for {link}: {rating_value}")
                else:
                    print(f"No rating value found for {link}.")
            else:
                print(f"No rating div found for {link}.")

            # Fetch Regulation Information
            regulation_status = 'No'  # Default value
            regulation_details = 'N/A'  # Default value
            regulation_divs = broker_soup.find_all('div', class_='span7')
            if regulation_divs:
                for div in regulation_divs:
                    regulation_text = div.get_text(separator=' ', strip=True)
                    print(f"Extracted text for {link}: {regulation_text}")

                    # Use regex to match "YES - " or "NO - " followed by any phrase
                    match = re.search(r'(YES|NO|NOT REGULATED)\s*-\s*(.+)', regulation_text)
                    if match:
                        regulation_status = match.group(1)  # "YES" or "NO"
                        regulation_details = match.group(2)  # Text after "YES - " or "NO - "
                        # Convert "NOT REGULATED" to "No"
                        if regulation_status == "NOT REGULATED":
                            regulation_status = "No"
                        print(f"Regulation for {link}: {regulation_status} - {regulation_details}")
                        break
            else:
                print(f"No regulation information found for {link}.")

            return regulation_status, regulation_details, rating_value

    except Exception as e:
        print(f"Error fetching regulation or rating info for {link}: {e}")
        return 'N/A', 'N/A'


def fetch_regulation_info(link, session):
    """Fetch regulation information from the broker's individual page."""
    try:
        # Attempt to fetch the page
        for attempt in range(3):  # Retry up to 3 times
            response = session.get(link, headers=headers)

            # If 403 error, handle it
            if response.status_code == 403:
                print(f"Access forbidden for {link}.")
                return '403 Forbidden'

            # Handle 202 processing status
            if response.status_code == 202:
                print(f"Request for {link} is still processing. Waiting before retrying...")
                time.sleep(5)  # Wait for 5 seconds before retrying
                continue  # Retry the request

            if response.status_code != 200:
                print(f"Failed to retrieve data for {link}, status code: {response.status_code}")
                return 'N/A'  # If the request fails, return 'N/A'

            # Parse the broker's page
            broker_soup = BeautifulSoup(response.text, 'html.parser')

            # Find all div elements with the class 'span7'
            regulation_divs = broker_soup.find_all('div', class_='span7')
            if regulation_divs:
                for div in regulation_divs:
                    # Extract all the text within this div
                    regulation_text = div.get_text(separator=' ', strip=True)

                    # Debugging line to show the extracted text
                    print(f"Extracted text for {link}: {regulation_text}")

                    # Use regex to match "YES - " or "NO - " followed by any phrase
                    match = re.search(r'(YES|NO|NOT REGULATED)\s*-\s*(.+)', regulation_text)

                    if match:
                        # If a match is found, return the full regulation information
                        regulation_status = match.group(1)  # "YES" or "NO"
                        regulation_details = match.group(2)  # The text after "YES - " or "NO - "
                        return f"{regulation_status} - {regulation_details}"

                # If no matching regulation text is found in any div
                print(f"No specific regulation text found for {link}.")
                return 'N/A'

            else:
                print(f"No regulation information found for {link}.")
                return 'N/A'

    except Exception as e:
        print(f"Error fetching regulation info for {link}: {e}")
        return 'N/A'


# Initialize a list to store broker data
brokers_data = []

# Find all rows in the table
rows = soup.find(id='tableList')

# Check if any rows were found
if not rows:
    print("No rows found in the table.")
else:
    # Extract data from each relevant row
    for row in rows.find_all('tr'):  # Ensure we iterate through each row
        broker_info = {}

        # Broker Name and Link
        name_button = row.find('button', class_='btn btn-default btn-block btn-lg')
        if name_button:
            broker_info['Name'] = name_button.text.split('|')[0].strip()
            relative_link = row.find('a', href=True)['href']  # Get link from the <a> tag wrapping the button
            broker_info['Link'] = homepage_url + relative_link  # Construct absolute URL

            # Fetch regulation information
            regulation_status,regulation_details,rating_value = fetch_rating_and_regulation_info(broker_info['Link'], session)
            broker_info['Regulation Status'] = regulation_status
            broker_info['Regulation Details'] = regulation_details
            broker_info['Rating'] = rating_value

        # Append the broker info to the list
        brokers_data.append(broker_info)

# Create a DataFrame
df = pd.DataFrame(brokers_data)

# Display the DataFrame
print(df)

# Optionally, save the DataFrame to a CSV file
df.to_csv('brokers_data.csv', index=False)
