#!/bin/zsh
set -euo pipefail

echo "[oncreate] Updating apt package index..."
sudo apt-get update -y

echo "[oncreate] Installing PortAudio development libraries for PyAudio..."
sudo apt-get install -y --no-install-recommends \
	portaudio19-dev \
	libasound2-dev \
	libjack-jackd2-dev || {
		echo "[oncreate] Warning: failed to install some audio dev libs" >&2
	}

echo "[oncreate] Installing project Python dependencies via Poetry..."
# poetry install --no-root

echo "[oncreate] Completed devcontainer setup."
