import subprocess

from descidb import chunker
import json
import ast

# def test_pipeline(config: dict, input_url: str) -> None:
#     """Test the pipeline with the specified configuration and input URL."""
#     # Convert the input URL
#     conversion_type = config["converter"]
#     chunking_type = config["chunker"]
#     embedding_type = config["embedder"]

#     build_command = "podman build --no-cache -t job-image -f ../docker/convert.Dockerfile"
#     subprocess.run(build_command, shell=True, check=True)

#     remove_command = "podman rm -f job-container"
#     subprocess.run(remove_command, shell=True, check=False)

#     run_command = (
#         f"podman run --rm --name job-container job-image {
#             conversion_type} {input_url}"
#     )
#     try:
#         result = subprocess.run(
#             run_command,
#             shell=True,
#             check=True,
#             capture_output=True,
#             text=True,
#         )
#         result = result.stdout
#     except subprocess.CalledProcessError as e:
#         print("Command failed:", e.stderr)

#     # Chunk the converted text
#     build_command = "podman build --no-cache -t job-image -f ../docker/chunk.Dockerfile"
#     subprocess.run(build_command, shell=True, check=True)

#     remove_command = "podman rm -f job-container"
#     subprocess.run(remove_command, shell=True, check=False)

#     run_command = (
#         f"podman run --rm --name job-container job-image {
#             chunking_type} {result}"
#     )

#     try:
#         result = subprocess.run(
#             run_command,
#             shell=True,
#             check=True,
#             capture_output=True,
#             text=True,
#         )
#         result = result.stdout
#     except subprocess.CalledProcessError as e:
#         print("Command failed:", e.stderr)


chunker_type = "sentence"
input_url = "https://gateway.lighthouse.storage/ipfs/bafkreies5jikyxatomqj2zrg5e7z2fpb5bd62zsgqqhkd2k5eorhy5jc2i"

converted = chunker.chunk_from_url(
    chunker_type=chunker_type, input_url=input_url
)

build_command = "podman build --no-cache -t job-image -f ../docker/chunk.Dockerfile"
subprocess.run(build_command, shell=True, check=True)

remove_command = "podman rm -f job-container"
subprocess.run(remove_command, shell=True, check=False)

run_command = (
    f"podman run --rm --name job-container job-image {
        chunker_type} {input_url}"
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
    print(raw_output)

    result_array = ast.literal_eval(raw_output)

    print(result_array[0])
    print(result_array)
except subprocess.CalledProcessError as e:
    print("Command failed:", e.stderr)


# embeder_type = "openai"
# ipfs_url = "https://gateway.lighthouse.storage/ipfs/bafkreies5jikyxatomqj2zrg5e7z2fpb5bd62zsgqqhkd2k5eorhy5jc2i"

# if False:
#     chunked = chunker.chunk_from_url(
#         chunker_type=chunker_type, input_url=ipfs_url)
#     print(chunked)

# build_command = "podman build --no-cache -t job-image -f ../docker/chunk.Dockerfile"
# subprocess.run(build_command, shell=True, check=True)

# remove_command = "podman rm -f job-container"
# subprocess.run(remove_command, shell=True, check=False)

# env_vars = {
#     "OPENAI_API_KEY": "sk-DkpEd31FQDPP4hycFq743IIT-QlFjXiRBeYZ7PVWWdT3BlbkFJl2elt0mENPhg4d7vlEFGucjoJ5rC_qGO3GsuP4ARsA",
# }

# env_flags = " ".join(f"-e {key}={value}" for key, value in env_vars.items())

# run_command = (
#     f"podman run --rm --name job-container {
#         env_flags} job-image {embeder_type} {ipfs_url}"
# )

# try:
#     result = subprocess.run(
#         run_command,
#         shell=True,
#         check=True,
#         capture_output=True,
#         text=True,
#     )
#     result = result.stdout

#     print(result)
# except subprocess.CalledProcessError as e:
#     print("Command failed:", e.stderr)
