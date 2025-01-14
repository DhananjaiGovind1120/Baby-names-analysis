import requests

# Port API Configuration
PORT_API_URL = "https://api.getport.io/v1"
PORT_API_TOKEN = "YOUR_API_KEY"  # Replace this with your Port API key
HEADERS = {
    "Authorization": f"Bearer {PORT_API_TOKEN}",
    "Content-Type": "application/json"
}

# Fetch all services
def fetch_services():
    url = f"{PORT_API_URL}/blueprints/service/entities"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["data"]

# Fetch related frameworks for a service
def fetch_related_frameworks(service_identifier):
    url = f"{PORT_API_URL}/blueprints/service/entities/{service_identifier}/relations/usedFrameworks"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["data"]

# Update the EOL package count for a service
def update_service_eol_count(service_identifier, eol_count):
    url = f"{PORT_API_URL}/blueprints/service/entities/{service_identifier}/properties"
    payload = {
        "eol_package_count": eol_count
    }
    response = requests.patch(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    print(f"Updated {service_identifier} with {eol_count} EOL frameworks.")

# Main logic
def main():
    # Fetch all services
    services = fetch_services()

    for service in services:
        service_identifier = service["identifier"]

        # Fetch related frameworks
        frameworks = fetch_related_frameworks(service_identifier)

        # Count EOL frameworks
        eol_count = sum(1 for fw in frameworks if fw["properties"]["state"] == "EOL")

        # Update the service entity with the EOL count
        update_service_eol_count(service_identifier, eol_count)

if __name__ == "__main__":
    main()
