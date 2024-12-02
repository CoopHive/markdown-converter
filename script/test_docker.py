import subprocess

build_command = "podman build -t job-image -f ../docker/convert.Dockerfile"
subprocess.run(build_command, shell=True, check=True)

conversion_type = "marker"
input_url = "https://gateway.lighthouse.storage/ipfs/bafkreidsulm4ma4jnkp2zc2zw64rpiqj6diemfimazo4bfkc5urguzql3u"

run_command = (
    f"podman run --rm --name job-container job-image {conversion_type} {input_url}"
)
result = subprocess.run(
    run_command,
    shell=True,
    check=True,
    capture_output=True,
    text=True,
)

result = result.stdout

print(result)
