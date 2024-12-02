import mimetypes
import tarfile
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import requests


def compress(list_of_input_paths: List[str], output_path: str):
    """Compresses the given list of input file paths into a tar file."""
    if not output_path.endswith(".tar"):
        output_path += ".tar"

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with tarfile.open(output_path, "w") as tar:
        for input_path in list_of_input_paths:
            input_path = Path(input_path)
            if not input_path.exists():
                print(f"Warning: {input_path} does not exist and will be skipped.")
                continue
            # Add the file or directory to the tar file
            tar.add(input_path, arcname=input_path.name)
            print(f"Added {input_path} as {input_path.name} to {output_path}")


def extract(tar_file_path: str, output_path: str):
    """Extracts the contents of a tar file to the specified output directory."""
    # Ensure the tar file exists
    tar_path = Path(tar_file_path)
    if not tar_path.exists():
        raise FileNotFoundError(f"The tar file '{tar_file_path}' does not exist.")

    # Ensure the output directory exists
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open the tar file and extract its contents
    with tarfile.open(tar_file_path, "r") as tar:
        print(f"Extracting {tar_file_path} to {output_path}...")
        tar.extractall(path=output_dir)
        print("Extraction complete.")


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


def download_from_url(url: str, output_folder: str):
    """Downloads a file from a given URL and saves it to the specified output path."""
    # Ensure the output folder exists
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch the file
    print(f"Downloading from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    parsed_url = urlparse(url)
    file_name = Path(parsed_url.path).name

    content_type = response.headers.get("content-type")
    extension = mimetypes.guess_extension(content_type) if content_type else ".bin"
    file_name = f"{file_name}{extension}"

    # Save the file in the output folder
    output_file = output_dir / file_name
    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"Downloaded file saved to {output_file}.")
    return str(output_file)
