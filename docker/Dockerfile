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

ENTRYPOINT ["python3", "-c", "import sys; from descidb.converter import convert; print(convert(*sys.argv[1:]))"]