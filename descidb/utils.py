import requests


def upload_to_lighthouse(filepath: str, ipfs_api_key: str) -> str:
    """Uploads a file to Lighthouse IPFS and returns the gateway url, via the file CID."""
    url = "https://node.lighthouse.storage/api/v0/add"
    headers = {"Authorization": f"Bearer {ipfs_api_key}"}
    with open(filepath, "rb") as file:
        files = {"file": file}
        print(f"Uploading {filepath} to Lighthouse IPFS...")
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
    cid = response.json()["Hash"]
    return f"https://gateway.lighthouse.storage/ipfs/{cid}"