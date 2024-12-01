import subprocess
import os

build_command = f"podman build -t job-image ../docker"
subprocess.run(build_command, shell=True, check=True)

pdf_path="/app/papers/desci.pdf"
conversion_type="marker"

papers_path = os.path.abspath('../papers/desci.pdf')

run_command = f"podman run --rm --name job-container -v {papers_path}:{pdf_path} job-image {conversion_type} {pdf_path}"
result = subprocess.run(
    run_command,
    shell=True,
    check=True,
    capture_output=True,
    text=True,
)

result = result.stdout


print(result)