import os
import sys
import argparse
import requests
import base64
import json
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Constants
VERCEL_API_BASE = "https://api.vercel.com"
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
VERCEL_TEAM = os.getenv("VERCEL_TEAM")

def get_deployment_id(domain):
    """Fetch deployment ID from deployment URL."""
    api_endpoint = f"{VERCEL_API_BASE}/v13/deployments/{domain}"
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}"
    }
    response = requests.get(api_endpoint, headers=headers)
    response.raise_for_status()
    deployment = response.json()
    return deployment["id"]

def get_deployment_files(deployment_id):
    """Fetch list of source files from deployment."""
    api_endpoint = f"{VERCEL_API_BASE}/v6/deployments/{deployment_id}/files"
    if VERCEL_TEAM:
        api_endpoint += f"?teamId={VERCEL_TEAM}"
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}"
    }
    response = requests.get(api_endpoint, headers=headers)
    response.raise_for_status()
    return response.json()

def download_file(deployment_id, file_id, destination):
    """Download file content and save to destination."""
    api_endpoint = f"{VERCEL_API_BASE}/v7/deployments/{deployment_id}/files/{file_id}"
    if VERCEL_TEAM:
        api_endpoint += f"?teamId={VERCEL_TEAM}"
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}"
    }
    response = requests.get(api_endpoint, headers=headers)
    response.raise_for_status()
    data = response.json()["data"]
    content = base64.b64decode(data)
    with open(destination, "wb") as f:
        f.write(content)

def flatten_tree(node, parent_path=Path("")):
    """Flatten the tree structure to list of files/dirs."""
    full_path = parent_path / node["name"]
    if node["type"] == "directory":
        os.makedirs(full_path, exist_ok=True)
        for child in node.get("children", []):
            flatten_tree(child, full_path)
    elif node["type"] == "file":
        download_file(
            deployment_id,
            node["uid"],
            full_path
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch source code from Vercel deployment.")
    parser.add_argument("deployment", help="Deployment URL or ID")
    parser.add_argument("destination", help="Destination directory", nargs="?", default=None)
    args = parser.parse_args()

    if not VERCEL_TOKEN:
        print("Error: Missing VERCEL_TOKEN in .env file.")
        sys.exit(1)

    deployment_input = args.deployment
    destination_dir = args.destination

    if not destination_dir:
        destination_dir = deployment_input

    # Determine deployment ID
    if deployment_input.startswith("dpl_"):
        deployment_id = deployment_input
    else:
        deployment_id = get_deployment_id(deployment_input)

    # Get source files
    files_response = get_deployment_files(deployment_id)
    source_node = next((item for item in files_response if item["name"] == "src"), None)
    if not source_node:
        print("Error: Source directory 'src' not found in deployment.")
        sys.exit(1)

    # Flatten tree and download files
    flatten_tree(source_node, Path(destination_dir))

    print(f"Source code fetched and saved to {destination_dir}")