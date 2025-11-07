#!/bin/bash

# ============================================================
# 🐳 AWS Lambda Deployment Script for NewsFinderBot (Docker-based)
# ============================================================
# This script:
# 1. Builds dependencies in an Amazon Linux 2 environment (Lambda-compatible)
# 2. Packages your source code and dependencies into a single .zip
# 3. Produces a deployment-ready ZIP file: Brieflybot-lambda.zip
# ============================================================

set -e  # Exit on any error

PACKAGE_NAME="Brieflybot-lambda"
DEPLOYMENT_DIR="lambda-deployment"
PACKAGE_DIR="package"
ZIP_FILE="${PACKAGE_NAME}.zip"
REQUIREMENTS_FILE="requirements-lambda.txt"

echo "🚀 Building AWS Lambda package using Docker (Amazon Linux 2)..."

# Validate requirements file exists
if [ ! -f "${REQUIREMENTS_FILE}" ]; then
    echo "❌ ERROR: '${REQUIREMENTS_FILE}' not found in current directory!"
    echo "Please make sure the file exists before running this script."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning up previous deployment..."
rm -rf "${DEPLOYMENT_DIR}" "${ZIP_FILE}"

# Create directories
echo "📁 Setting up directories..."
mkdir -p "${DEPLOYMENT_DIR}/${PACKAGE_DIR}"

# Copy project files
echo "📋 Copying source code..."
cp lambda_function.py main.py "${DEPLOYMENT_DIR}/"
cp -r slackbot "${DEPLOYMENT_DIR}/"
cp "${REQUIREMENTS_FILE}" "${DEPLOYMENT_DIR}/"  # ✅ Copy requirements inside

# Build dependencies inside Amazon Linux 2 Docker container
echo "🐳 Installing dependencies inside Amazon Linux 2 Docker..."
docker run --rm -v "$(pwd)/${DEPLOYMENT_DIR}":/var/task -w /var/task amazonlinux:2 bash -c "
    set -e
    echo '📦 Installing system dependencies...'
    yum install -y python3 python3-pip python3-devel zip gcc rust cargo >/dev/null
    python3 -m pip install --upgrade pip
    echo '⬇️ Installing Python packages from requirements-lambda.txt...'
    pip3 install --target ./package -r requirements-lambda.txt
"

# Create the zip package
echo "🗜️ Creating deployment package..."
cd "${DEPLOYMENT_DIR}"
cd "${PACKAGE_DIR}"
zip -r ../${ZIP_FILE} . >/dev/null
cd ..
zip ${ZIP_FILE} lambda_function.py main.py >/dev/null
zip -r ${ZIP_FILE} slackbot/ >/dev/null
mv ${ZIP_FILE} ../

# Clean up
cd ..
rm -rf "${DEPLOYMENT_DIR}"

echo ""
echo "✅ Deployment package created successfully: ${ZIP_FILE}"
echo "📊 Package size: $(du -h ${ZIP_FILE} | cut -f1)"
echo ""
echo "🚀 Ready to deploy to AWS Lambda!"
echo ""
echo "Next steps:"
echo "1️⃣ Upload ${ZIP_FILE} to AWS Lambda"
echo "2️⃣ Set handler to: lambda_function.lambda_handler"
echo "3️⃣ Configure environment variables:"
echo "   - NEWSAPI_KEY"
echo "   - OPENAI_API_KEY or GEMINI_API_KEY"
echo "   - SLACK_BOT_TOKEN"
echo "   - SLACK_APP_TOKEN"
echo "   - SLACK_CHANNEL_ID"
echo "4️⃣ Set timeout ≥ 300s and memory ≥ 512 MB"
