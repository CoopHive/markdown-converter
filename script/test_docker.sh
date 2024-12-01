podman build -t job-image ../docker

podman run --rm --name job-container job-image

# TODO: make result generic to volume, now defaulting to output of job being string.
# result = result.stdout