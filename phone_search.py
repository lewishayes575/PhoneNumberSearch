import requests
import phonenumbers
from phonenumbers import geocoder, carrier
import os
import json

CONFIG_FILE = "api_keys.json"

# Function to save API keys
def save_api_keys(api_keys):
    with open(CONFIG_FILE, "w") as file:
        json.dump(api_keys, file)

# Function to load API keys
def load_api_keys():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to get API Key from user
def get_api_key(service_name):
    api_keys = load_api_keys()
    if service_name in api_keys:
        return api_keys[service_name]
    api_key = input(f"Enter your {service_name} API Key: ")
    api_keys[service_name] = api_key
    save_api_keys(api_keys)
    return api_key

# Function to validate phone number
def validate_number(number):
    try:
        parsed_number = phonenumbers.parse(number)
        return phonenumbers.is_valid_number(parsed_number)
    except:
        return False

# Function to get phone number details
def get_number_info(number, api_key, open_cell_id_api_key):
    try:
        parsed_number = phonenumbers.parse(number)
        country = geocoder.description_for_number(parsed_number, "en")
        carrier_name = carrier.name_for_number(parsed_number, "en")
        
        print(f"\nBasic Info:")
        print(f"Country: {country}")
        print(f"Carrier: {carrier_name}")
        
        # Using NumVerify API for additional details
        url = f"http://apilayer.net/api/validate?access_key={api_key}&number={number}&format=1"
        response = requests.get(url)
        data = response.json()
        
        if data.get("valid"):
            print("\nAdditional Details from API:")
            print(f"Location: {data.get('location')}")
            print(f"Line Type: {data.get('line_type')}")
            print(f"International Format: {data.get('international_format')}")
        else:
            print("\nAPI could not validate the number.")
        
        # Getting possible cell tower location using OpenCelliD API
        if open_cell_id_api_key:
            mcc = data.get('country_code')  # Mobile Country Code
            mnc = data.get('carrier')  # Mobile Network Code
            lac = data.get('location')  # Location Area Code
            cid = data.get('line_type')  # Cell ID (simulated)
            
            if mcc and mnc and lac and cid:
                cell_tower_url = f"https://opencellid.org/cell/get?key={open_cell_id_api_key}&mcc={mcc}&mnc={mnc}&lac={lac}&cid={cid}"
                cell_response = requests.get(cell_tower_url)
                cell_data = cell_response.json()
                if 'lat' in cell_data and 'lon' in cell_data:
                    print(f"\nEstimated Cell Tower Location:")
                    print(f"Latitude: {cell_data['lat']}")
                    print(f"Longitude: {cell_data['lon']}")
                else:
                    print("\nCould not determine cell tower location.")
            else:
                print("\nNot enough data to determine possible cell tower.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    numverify_api_key = get_api_key("NumVerify")
    open_cell_id_api_key = get_api_key("OpenCelliD")
    phone_number = input("Enter phone number with country code (e.g., +14155552671): ")
    
    if validate_number(phone_number):
        get_number_info(phone_number, numverify_api_key, open_cell_id_api_key)
    else:
        print("Invalid phone number. Please enter a correct number.")
