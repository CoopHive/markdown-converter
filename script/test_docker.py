import subprocess

from descidb import converter
from descidb import chunker

if False:
    conversion_type = "marker"
    input_url = "https://gateway.lighthouse.storage/ipfs/bafkreidsulm4ma4jnkp2zc2zw64rpiqj6diemfimazo4bfkc5urguzql3u"

    converted = converter.convert_from_url(
        conversion_type=conversion_type, input_url=input_url
    )

    build_command = "podman build --no-cache -t job-image -f ../docker/convert.Dockerfile"
    subprocess.run(build_command, shell=True, check=True)

    remove_command = "podman rm -f job-container"
    subprocess.run(remove_command, shell=True, check=False)

    run_command = (
        f"podman run --rm --name job-container job-image {conversion_type} {input_url}"
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

        print(result)
    except subprocess.CalledProcessError as e:
        print("Command failed:", e.stderr)


chunker_type = "paragraph"
ipfs_url = "https://gateway.lighthouse.storage/ipfs/bafkreidt4eler4fphoz7k5s6f6lx7myvz5b4hwsvd7v7spymd2iob6qvwy"

if False:
    chunked = chunker.chunk_from_url(chunker_type=chunker_type, input_url=ipfs_url)
    print(chunked)

build_command = "podman build --no-cache -t job-image -f ../docker/chunk.Dockerfile"
subprocess.run(build_command, shell=True, check=True)

remove_command = "podman rm -f job-container"
subprocess.run(remove_command, shell=True, check=False)

run_command = (
    f"podman run --rm --name job-container job-image {chunker_type} {ipfs_url}"
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

    print(result)
except subprocess.CalledProcessError as e:
    print("Command failed:", e.stderr)