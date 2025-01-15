import requests
import os

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
    url = f"{PORT_API_URL}/blueprints/service/entities/{service_identifier}/relation/used_frameworks"
    response = requests.get(url, headers=HEADERS)
    print(f"Fetching frameworks for service '{service_identifier}': Status Code {response.status_code}")
    print(f"Response: {response.text}")
    response.raise_for_status()

    try:
        return response.json()["entities"]  
    except KeyError:
        raise ValueError(f"Unexpected response format while fetching frameworks for service '{service_identifier}': {response.json()}")

# Update the EOL package count for a service
def update_service_eol_count(service_identifier, eol_count):
    url = f"{PORT_API_URL}/blueprints/service/entities/{service_identifier}/properties"
    payload = {
        "properties": {  # Added the 'properties' key
            "eol_count": eol_count  # Nested the 'eol_count' inside 'properties'
        }
    }
    response = requests.patch(url, json=payload, headers=HEADERS)
    print(f"Updating service '{service_identifier}': Status Code {response.status_code}")
    print(f"Response: {response.text}")
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
            frameworks = fetch_related_frameworks(service_identifier)

            # Count EOL frameworks
            eol_count = sum(1 for fw in frameworks if fw["properties"].get("state") == "EOL")

            # Update the service entity with the EOL count
            update_service_eol_count(service_identifier, eol_count)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
