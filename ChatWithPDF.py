import requests

# Define the search parameters
params = {
    'q': '"vless://"" vmess://""',  # Search for repositories containing both "vless://" and "vmess://"
    'sort': 'stars',  # Sort results by stars (optional)
    'order': 'desc',  # Order results descending (optional)
    'per_page': 100,  # Number of items per page (max 100)
}

# Make the request to the GitHub API
response = requests.get('https://api.github.com/search/code', params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Print the total count of matching repositories
    print(f"Total matches found: {data['total_count']}")
    
    # Iterate through the results and print repository names
    for item in data['items']:
        print(item['repository']['full_name'])
else:
    print("Failed to fetch data:", response.status_code)
