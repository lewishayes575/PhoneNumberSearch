import requests
import phonenumbers
from phonenumbers import geocoder, carrier
import os
import json
import subprocess
import time

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

# Function to detect incoming calls using Termux API
def detect_incoming_call():
    try:
        while True:
            result = subprocess.run(["termux-telephony-callinfo"], capture_output=True, text=True)
            if result.returncode == 0:
                call_data = json.loads(result.stdout)
                phone_number = call_data.get("phone_number", "")
                if phone_number:
                    print(f"Incoming call detected from: {phone_number}")
                    return phone_number
            time.sleep(2)  # Check for calls every 2 seconds
    except Exception as e:
        print(f"Error detecting incoming call: {e}")
    return None

# Function to get cell tower info from Termux API
def get_cell_tower_info():
    try:
        result = subprocess.run(["termux-telephony-cellinfo"], capture_output=True, text=True)
        if result.returncode == 0:
            cell_data = json.loads(result.stdout)
            mcc = str(cell_data[0].get("mcc", ""))
            mnc = str(cell_data[0].get("mnc", ""))
            lac = str(cell_data[0].get("lac", ""))
            cid = str(cell_data[0].get("cid", ""))
            return mcc, mnc, lac, cid
        else:
            print("Error fetching cell tower info. Make sure Termux API is installed and has the necessary permissions.")
    except Exception as e:
        print(f"Error retrieving cell tower info: {e}")
    return None, None, None, None

# Function to get phone number details
def get_number_info(number, numverify_api_key, opencellid_api_key):
    try:
        parsed_number = phonenumbers.parse(number)
        country = geocoder.description_for_number(parsed_number, "en")
        carrier_name = carrier.name_for_number(parsed_number, "en")
        
        print(f"\nBasic Info:")
        print(f"Country: {country}")
        print(f"Carrier: {carrier_name}")
        
        # Using NumVerify API for additional details
        url = f"http://apilayer.net/api/validate?access_key={numverify_api_key}&number={number}&format=1"
        response = requests.get(url)
        data = response.json()
        
        if data.get("valid"):
            print("\nAdditional Details from API:")
            print(f"Location: {data.get('location')}")
            print(f"Line Type: {data.get('line_type')}")
            print(f"International Format: {data.get('international_format')}")
        else:
            print("\nAPI could not validate the number.")
        
        # Get cell tower data from Termux API
        print("\nFetching cell tower location...")
        mcc, mnc, lac, cid = get_cell_tower_info()
        
        if mcc and mnc and lac and cid:
            cell_tower_url = f"https://opencellid.org/cell/get?key={opencellid_api_key}&mcc={mcc}&mnc={mnc}&lac={lac}&cid={cid}"
            cell_response = requests.get(cell_tower_url)
            cell_data = cell_response.json()
            
            if 'lat' in cell_data and 'lon' in cell_data:
                print(f"\nEstimated Cell Tower Location:")
                print(f"Latitude: {cell_data['lat']}")
                print(f"Longitude: {cell_data['lon']}")
            else:
                print("\nCould not determine cell tower location. Check the MCC, MNC, LAC, and CID values.")
        else:
            print("\nUnable to retrieve cell tower data from Termux. Ensure you have granted necessary permissions.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if check_existing_api_keys():
        print("API keys found. Skipping API key input.")
        api_keys = load_api_keys()
        numverify_api_key = api_keys.get("NumVerify", "")
        opencellid_api_key = api_keys.get("OpenCelliD", "")
    else:
        numverify_api_key = get_api_key("NumVerify")
        opencellid_api_key = get_api_key("OpenCelliD")
    
    print("Waiting for an incoming call...")
    phone_number = detect_incoming_call()
    
    if phone_number:
        get_number_info(phone_number, numverify_api_key, opencellid_api_key)
    else:
        print("No incoming call detected.")
