# podman build -t job-image docker
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    postgresql libpq-dev \
    gcc \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && pip install --no-cache-dir uv

RUN uv pip install "git+https://github.com/CoopHive/markdown-converter.git@conversion" --system

ENTRYPOINT ["/usr/local/bin/python", "/usr/local/lib/python3.12/site-packages/descidb/test.py"]

# Run the package or set a default command
# CMD ["python", "-m", "<your_package_entry_point>"]
