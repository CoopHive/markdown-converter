import subprocess

from descidb import chunker
from descidb import utils
import json
import ast
import re
import os
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


def run_conversion(conversion_type: str, input_url: str) -> str:
    """Run the conversion process with the specified type and input URL."""

    build_command = "podman build --no-cache -t job-image -f ../docker/convert.Dockerfile"
    subprocess.run(build_command, shell=True, check=True)

    remove_command = "podman rm -f job-container"
    subprocess.run(remove_command, shell=True, check=False)

    run_command = (
        f"podman run - -rm - -name job-container job-image {
            conversion_type} {input_url}"
    )
    try:
        result = subprocess.run(
            run_command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )
        result = result.stdout
        return result
    except subprocess.CalledProcessError as e:
        print("Command failed:", e.stderr)


def run_chunking(chunking_type: str, input_url: str) -> str:
    build_command = "podman build --no-cache -t job-image -f ../docker/chunk.Dockerfile"
    subprocess.run(build_command, shell=True, check=True)

    remove_command = "podman rm -f job-container"
    subprocess.run(remove_command, shell=True, check=False)

    run_command = (
        f"podman run - -rm - -name job-container job-image {
            chunking_type} {input_url}"
    )
    try:
        result = subprocess.run(
            run_command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )
        raw_output = result.stdout.strip()
        match = re.search(r"\[.*\]", raw_output, flags=re.DOTALL)
        array_str = match.group(0)
        result_array = ast.literal_eval(array_str)
        return result_array
    except subprocess.CalledProcessError as e:
        print("Command failed:", e.stderr)


def run_embedding(embedding_type: str, input_url: str) -> str:

    build_command = "podman build --no-cache -t job-image -f ../docker/embed.Dockerfile"
    subprocess.run(build_command, shell=True, check=True)

    remove_command = "podman rm -f job-container"
    subprocess.run(remove_command, shell=True, check=False)

    env_vars = {
        "OPENAI_API_KEY": "",
    }

    env_flags = " ".join(f"-e {key}={value}" for key,
                         value in env_vars.items())

    run_command = (
        f"podman run --rm --name job-container {env_flags} job-image {embedding_type} {input_url}")

    try:
        result = subprocess.run(
            run_command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )
        result = result.stdout.strip()
        return result
    except subprocess.CalledProcessError as e:
        print("Command failed:", e.stderr)


def _test_pipeline(config: dict, input_url: str) -> None:
    """Test the pipeline with the specified configuration and input URL."""
    conversion_type = config["converter"]
    chunking_type = config["chunker"]
    embedding_type = config["embedder"]
    lighthouse_api_key = ""

    # Run the conversion process
    output = run_conversion(
        conversion_type=conversion_type, input_url=input_url)

    # Upload to LightHouse IPFS
    ipfs_url_chunked = utils.upload_to_lighthouse(output, lighthouse_api_key)

    # Run the chunking process
    chunked = run_chunking(
        chunking_type=chunking_type, input_url=ipfs_url_chunked)

    # Upload to LightHouse IPFS - each Chunk as a seperate Job
    ipfs_url_chunked = []
    for chunk in chunked:
        file_name = "temp_file.txt"
        with open(file_name, "w") as file:
            file.write(chunk)
        chunk_path = os.path.abspath(file_name)
        chunk_url = upload_to_lighthouse(chunk_path, lighthouse_api_key)
        ipfs_url_chunked.append(chunk_url)
        os.remove(chunk_path)

    chunks_to_embeddings = {}

    # Run the embedding process for each chunk and upload to LightHouse IPFS
    for url in ipfs_url_chunked:
        embedding = run_embedding(embedding_type=embedding_type, input_url=url)
        file_name = "temp_file.txt"
        with open(file_name, "w") as file:
            file.write(embedding)
        embedding_path = os.path.abspath(file_name)
        embedding_url = upload_to_lighthouse(
            embedding_path, lighthouse_api_key)
        chunks_to_embeddings[url] = embedding_url
        os.remove(embedding_path)


if __name__ == "__main__":
    config = {
        "converter": "openai",
        "chunker": "sentence",
        "embedder": "openai",
    }
    input_url = "https://gateway.lighthouse.storage/ipfs/bafkreies5jikyxatomqj2zrg5e7z2fpb5bd62zsgqqhkd2k5eorhy5jc2i"
    _test_pipeline(config, input_url)
