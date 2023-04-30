#!/usr/bin/env python3

import requests
import json
import jwt
import time
from pathlib import Path


def get_mailchimp_subscribers(mailchimp_url, api_key):
    subscribers = []
    count = 100
    offset = 0

    while True:
        paginated_url = f"{mailchimp_url}?count={count}&offset={offset}"
        response = requests.get(paginated_url, auth=('apikey', api_key), headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            members = response.json()['members']
            if not members:
                break

            subscribers.extend(members)
            offset += count
        else:
            print(f'Failed to fetch subscribers from Mailchimp, status code: {response.status_code}')
            break

    return subscribers


# Replace with your own API keys and list ID
MAILCHIMP_API_KEY = 'your_mailchimp_api_key'
MAILCHIMP_LIST_ID = 'your_mailchimp_list_id'
MAILCHIMP_DC = 'usX'  # Replace 'usX' with your Mailchimp data center
ISSUER_ID = 'your_issuer_id'
KEY_ID = 'your_key_id'
PRIVATE_KEY_FILE = 'path/to/your/private_key_file.p8'

# Mailchimp API URL for list members
mailchimp_members_url = f'https://{MAILCHIMP_DC}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members'

# App Store Connect API URL for testers and beta groups
app_store_testers_url = 'https://api.appstoreconnect.apple.com/v1/betaTesters'
app_store_beta_groups_url = 'https://api.appstoreconnect.apple.com/v1/betaGroups'

# Read the contents of the private key as a file 
private_key = Path(PRIVATE_KEY_FILE).read_text()

# Read the contents of the private key as an environment object
# private_key = os.environ.get('APP_STORE_PRIVATE_KEY')


# Set the expiration time for the JWT token (e.g., 20 minutes)
expiration_time = int(time.time()) + 1200

# Generate the JWT token
jwt_token = jwt.encode(
    {
        'iss': ISSUER_ID,
        'exp': expiration_time,
        'aud': 'appstoreconnect-v1'
    },
    private_key,
    algorithm='ES256',
    headers={'kid': KEY_ID}
)

headers = {
    'Authorization': f'Bearer {jwt_token}',
    'Content-Type': 'application/json',
}

# Get the Beta Group ID
response = requests.get(app_store_beta_groups_url, headers=headers)
if response.status_code == 200:
    beta_groups = response.json()['data']
    beta_group_id = None

    # Replace 'Your_Beta_Group_Name' with the name of the beta group you want to use
    for group in beta_groups:
        if group['attributes']['name'] == 'Your_Beta_Group_Name':
            beta_group_id = group['id']
            break

    if not beta_group_id:
        print("Beta Group not found.")
else:
    print(f'Failed to fetch beta groups from App Store Connect, status code: {response.status_code}, response: {response.content}')

# Get Mailchimp subscribers
mailchimp_subscribers = get_mailchimp_subscribers(mailchimp_members_url, MAILCHIMP_API_KEY)
subscriber_emails = {subscriber['email_address'] for subscriber in mailchimp_subscribers}

# Get TestFlight testers
response = requests.get(app_store_testers_url, headers=headers)
if response.status_code == 200:
    testers = response.json()['data']
    tester_emails = {tester['attributes']['email'] for tester in testers}

    # Find subscribers not in TestFlight
    new_testers = subscriber_emails - tester_emails

    # Add new testers to TestFlight
    for email in new_testers:        
        data = {
						'data': {
								'type': 'betaTesters',
								'attributes': {
										'email': email,
										'firstName': '',
										'lastName': ''
								},
								'relationships': {
										'betaGroups': {
												'data': [
														{
																'type': 'betaGroups',
																'id': beta_group_id
														}
												]
										}
								}
						}
				}
        response = requests.post(app_store_testers_url, headers=headers, data=json.dumps(data))

        if response.status_code == 201:
            print(f'Successfully added {email} to TestFlight')
        else:
            print(f'Failed to add {email} to TestFlight')
else:
    print('Failed to fetch testers from App Store Connect')
