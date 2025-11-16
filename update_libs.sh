#!/bin/bash
# Script to update bundled libraries using pip
# This installs libraries into chinese/lib/ for bundling with the addon

set -e

ADDON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${ADDON_DIR}/chinese/lib"

# Detect pip command (try python3 -m pip first, then pip3, then pip)
if command -v python3 &> /dev/null && python3 -m pip --version &> /dev/null; then
    PIP_CMD="python3 -m pip"
elif command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "Error: pip not found. Please install pip first."
    exit 1
fi

echo "Using: ${PIP_CMD}"
echo "Updating libraries in ${LIB_DIR}..."

# Ensure lib directory exists
mkdir -p "${LIB_DIR}"

# Install/update libraries using pip
# Use --target to install into lib directory
# Use --upgrade to update existing packages
# Use --no-deps if you want to manage dependencies manually

echo "Installing gtts..."
${PIP_CMD} install --target "${LIB_DIR}" --upgrade gtts

echo "Installing jieba..."
${PIP_CMD} install --target "${LIB_DIR}" --upgrade jieba

# Note: urllib3, chardet, certifi, idna are dependencies that will be installed automatically
# If you want to update them explicitly:
# ${PIP_CMD} install --target "${LIB_DIR}" --upgrade urllib3 chardet certifi idna

echo "Cleaning up..."
# Remove unnecessary files to reduce size
find "${LIB_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${LIB_DIR}" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "${LIB_DIR}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "${LIB_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true

echo "Done! Libraries updated in ${LIB_DIR}"
echo "Remember to test the addon before committing changes."

