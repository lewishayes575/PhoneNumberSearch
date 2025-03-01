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

# Function to check if API keys exist
def check_existing_api_keys():
    return os.path.exists(CONFIG_FILE)

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
def get_number_info(number, api_key):
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
        
        # Inform user about cell tower tracking limitations
        print("\nCell tower location tracking requires direct access to mobile network logs, which is not available via NumVerify API.")
        print("For accurate cell tower location, use a mobile app that can access real-time network data.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if check_existing_api_keys():
        print("API keys found. Skipping API key input.")
        api_keys = load_api_keys()
        numverify_api_key = api_keys.get("NumVerify", "")
    else:
        numverify_api_key = get_api_key("NumVerify")
    
    phone_number = input("Enter phone number with country code (e.g., +14155552671): ")
    
    if validate_number(phone_number):
        get_number_info(phone_number, numverify_api_key)
    else:
        print("Invalid phone number. Please enter a correct number.")
