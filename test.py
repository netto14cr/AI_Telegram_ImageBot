import os
import requests

# Limewire API configuration
LIMEWIRE_API_KEY = 'your-limewire-api-key'  # Replace 'your-limewire-api-key' with your actual API key
url = "https://api.limewire.com/api/image/generation"

# Prompt to generate an image
prompt = "a lion in space"

# HTTP request headers
headers = {
    "Authorization": f"Bearer {LIMEWIRE_API_KEY}",  # Include the API key in the authorization header
    "Content-Type": "application/json"  # Specify the content type as JSON
}

# HTTP request data
data = {
    "prompt": prompt  # Set the 'prompt' field in the request data to the specified prompt
}

# Make a POST request to the Limewire API
response = requests.post(url, headers=headers, json=data)

# Check if the request was successful
if response.status_code == 200:
    # Get the generated image URL from the API response
    image_url = response.json()['data'][0]['asset_url']
    # Print the generated image URL to the console
    print("Generated Image URL:", image_url)
else:
    # Print an error message if the request failed
    print("Failed to generate image. Status code:", response.status_code)
