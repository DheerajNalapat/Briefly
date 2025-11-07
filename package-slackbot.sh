#!/bin/bash

# ============================================================
# 🧱 Build Script: Slackbot Layer for AWS Lambda
# ============================================================
# This script packages the slackbot/ folder into a Lambda layer
# compatible with Python 3.12.
# ============================================================

set -e

LAYER_NAME="slackbot-layer"
LAYER_DIR="layer"
PYTHON_DIR="${LAYER_DIR}/python"
ZIP_FILE="${LAYER_NAME}.zip"

echo "🚀 Building Slackbot layer..."

# Clean old build
rm -rf "${LAYER_DIR}" "${ZIP_FILE}"

# Create directory structure for Lambda layer
mkdir -p "${PYTHON_DIR}"

# Copy your slackbot package
cp -r ./slackbot "${PYTHON_DIR}/"

# Zip it up
cd "${LAYER_DIR}"
zip -r "../${ZIP_FILE}" .
cd ..

# Show size
echo "✅ Slackbot layer package created: ${ZIP_FILE}"
echo "📦 Size: $(du -h ${ZIP_FILE} | cut -f1)"

echo ""
echo "🪣 To upload this layer, run:"
echo "aws lambda publish-layer-version \\"
echo "  --layer-name ${LAYER_NAME} \\"
echo "  --compatible-runtimes python3.12 \\"
echo "  --zip-file fileb://${ZIP_FILE}"
