import requests
import phonenumbers
from phonenumbers import geocoder, carrier
import os

# Function to get API Key from user
def get_api_key():
    api_key = input("Enter your NumVerify API Key (get it from https://numverify.com/): ")
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
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    api_key = get_api_key()
    phone_number = input("Enter phone number with country code (e.g., +14155552671): ")
    
    if validate_number(phone_number):
        get_number_info(phone_number, api_key)
    else:
        print("Invalid phone number. Please enter a correct number.")
