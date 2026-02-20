#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="gpx-racer:local"

docker build -t "${IMAGE_NAME}" .
docker run --rm -p 8501:8501 "${IMAGE_NAME}"
