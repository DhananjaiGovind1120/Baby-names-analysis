import requests
import os
import urllib.parse

# Port API Configuration
PORT_API_URL = "https://api.getport.io/v1"
PORT_API_TOKEN = os.environ.get("PORT_API_TOKEN")

# Validate API token
if not PORT_API_TOKEN:
    raise ValueError("PORT_API_TOKEN environment variable is not set!")

# Ensure the token includes "Bearer" prefix
if not PORT_API_TOKEN.startswith("Bearer "):
    PORT_API_TOKEN = f"Bearer {PORT_API_TOKEN}"

HEADERS = {
    "Authorization": PORT_API_TOKEN,
    "Content-Type": "application/json"
}

# Fetch all services
def fetch_services():
    url = f"{PORT_API_URL}/blueprints/service/entities"
    response = requests.get(url, headers=HEADERS)
    print(f"Fetching services: Status Code {response.status_code}")
    print(f"Response: {response.text}")
    response.raise_for_status()

    try:
        return response.json()["entities"]
    except KeyError:
        raise ValueError(f"Unexpected response format while fetching services: {response.json()}")

# Fetch related frameworks for a service
def fetch_related_frameworks(service_identifier):
    # Encode service identifier to handle special characters
    encoded_identifier = urllib.parse.quote(service_identifier)

    # Construct the correct URL for fetching the service entity
    url = f"{PORT_API_URL}/blueprints/service/entities/{encoded_identifier}"

    # Debug: Print the constructed URL
    print(f"Constructed URL: {url}")

    # Make the API request
    response = requests.get(url, headers=HEADERS)

    # Debug: Print the status code and response
    print(f"Fetching service '{service_identifier}': Status Code {response.status_code}")
    print(f"Response: {response.text}")

    # Raise an error for non-successful status codes
    response.raise_for_status()

    # Parse the response and extract the 'used_frameworks' relation
    try:
        return response.json()["entity"]["relations"]["used_frameworks"]
    except KeyError:
        raise ValueError(f"Unexpected response format while fetching frameworks for service '{service_identifier}': {response.json()}")

# Fetch framework details
def fetch_framework_details(framework_identifier):
    # Construct the URL for the framework entity
    url = f"{PORT_API_URL}/blueprints/framework/entities/{framework_identifier}"
    response = requests.get(url, headers=HEADERS)

    # Debug: Print the response status and content
    print(f"Fetching details for framework '{framework_identifier}': Status Code {response.status_code}")
    print(f"Response: {response.text}")

    # Raise an error for non-successful status codes
    response.raise_for_status()

    # Parse the framework details
    try:
        return response.json()["entity"]
    except KeyError:
        raise ValueError(f"Unexpected response format for framework '{framework_identifier}': {response.json()}")

# Update the EOL package count for a service
def update_service_eol_count(service_identifier, eol_count):
    # Construct the correct URL
    url = f"{PORT_API_URL}/blueprints/service/entities/{service_identifier}/properties/eol_count"
    
    # Payload for updating the property
    payload = {
        "value": eol_count
    }
    
    # Make the PATCH request
    response = requests.patch(url, json=payload, headers=HEADERS)
    
    # Debugging logs
    print(f"Updating service '{service_identifier}': Status Code {response.status_code}")
    print(f"Response: {response.text}")
    
    # Raise an error for non-successful status codes
    response.raise_for_status()
    
    print(f"Successfully updated {service_identifier} with {eol_count} EOL frameworks.")

# Main logic
def main():
    try:
        # Fetch all services
        services = fetch_services()

        for service in services:
            service_identifier = service.get("identifier")
            if not service_identifier:
                print(f"Skipping service with missing identifier: {service}")
                continue

            # Fetch related frameworks
            framework_ids = fetch_related_frameworks(service_identifier)

            # Count EOL frameworks
            eol_count = 0
            for fw_id in framework_ids:
                framework_details = fetch_framework_details(fw_id)
                if framework_details["properties"].get("state") == "EOL":
                    eol_count += 1

            # Update the service entity with the EOL count
            update_service_eol_count(service_identifier, eol_count)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
