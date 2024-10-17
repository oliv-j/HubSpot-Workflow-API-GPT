#!/usr/bin/env python3

import json
import requests
import pandas as pd
import os
import sys
import time
import keyring  # Import the keyring library

# Configuration
SERVICE_NAME = "keychain-item-label"  # The name you used when storing the token
USERNAME = "username"                # The username you used when storing the token
OUTPUT_FILE = "~/Downloads/flows/all_flow_content.csv"

# Retrieve the API token from the macOS Keychain using keyring
API_TOKEN = keyring.get_password(SERVICE_NAME, USERNAME)

if not API_TOKEN:
    print(f"Error: No API token found for service '{SERVICE_NAME}' and username '{USERNAME}'.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}
FLAWS_ENDPOINT = "https://api.hubapi.com/automation/v4/flows"
LIMIT = 100  # Number of flows per request

def fetch_all_flows():
    """
    Fetch all flows from HubSpot API, handling pagination.
    Returns a list of flow dictionaries.
    """
    all_flows = []
    after = None
    page = 1

    while True:
        params = {
            "limit": LIMIT
        }
        if after:
            params["after"] = after

        print(f"Fetching page {page} of flows...")
        response = requests.get(FLAWS_ENDPOINT, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch flows: {response.status_code} {response.text}")
            sys.exit(1)
        
        data = response.json()
        flows = data.get("results", [])
        all_flows.extend(flows)
        print(f"Retrieved {len(flows)} flows from page {page}.")

        if data.get("hasMore"):
            after = data.get("offset")  # or 'after' depending on the API's response
            page += 1
            # Optional: Sleep to respect rate limits
            time.sleep(0.2)  # Adjust sleep duration as needed
        else:
            print("All flows have been fetched.")
            break

    print(f"Total flows fetched: {len(all_flows)}")
    return all_flows

def fetch_flow_details(flow_id):
    """
    Fetch detailed information for a specific flow.
    """
    url = f"https://api.hubapi.com/automation/v4/flows/{flow_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch details for flow ID {flow_id}: {response.status_code} {response.text}")
        return None

def extract_flow_data(flow):
    """
    Extract required fields from detailed flow data.
    """
    # Extract required fields
    flow_id = flow.get("id", "")
    name = flow.get("name", "")
    is_enabled = flow.get("isEnabled", False)
    flow_type = flow.get("flowType", "")
    created_at = flow.get("createdAt", "")
    updated_at = flow.get("updatedAt", "")
    revision_id = flow.get("revisionId", "")
    
    # Extract actions; assuming 'actions' is a list or dict
    actions = flow.get("actions", [])
    # Convert actions to JSON string to store in CSV
    actions_str = json.dumps(actions)
    
    return {
        "id": flow_id,
        "name": name,
        "isEnabled": is_enabled,
        "flowType": flow_type,
        "createdAt": created_at,
        "updatedAt": updated_at,
        "revisionId": revision_id,
        "actions": actions_str
    }

def main():
    # Fetch all flows with pagination
    all_flows = fetch_all_flows()
    if not all_flows:
        print("No flows found.")
        sys.exit(1)

    print("Fetching detailed information for each flow...")
    all_flow_data = []
    total_flows = len(all_flows)
    
    for index, flow in enumerate(all_flows, start=1):
        flow_id = flow.get("id")
        if not flow_id:
            print(f"Flow at index {index} does not have an ID. Skipping.")
            continue
        
        detailed_flow = fetch_flow_details(flow_id)
        if detailed_flow:
            flow_data = extract_flow_data(detailed_flow)
            all_flow_data.append(flow_data)
        
        # Optional: Sleep to respect rate limits
        time.sleep(0.1)  # Adjust sleep duration as needed
        
        # Progress indicator
        if index % 10 == 0 or index == total_flows:
            print(f"Processed {index}/{total_flows} flows.")

    if not all_flow_data:
        print("No detailed flow data to write to CSV.")
        sys.exit(1)

    # Create DataFrame
    df = pd.DataFrame(all_flow_data, columns=["id", "name", "isEnabled", "flowType", "createdAt", "updatedAt", "revisionId", "actions"])

    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"All flow data has been saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()