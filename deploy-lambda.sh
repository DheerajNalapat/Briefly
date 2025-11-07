#!/bin/bash

# AWS Lambda Deployment Script for NewsFinderBot
# This script creates a deployment package for AWS Lambda

set -e  # Exit on any error

echo "🚀 Creating AWS Lambda deployment package for NewsFinderBot..."

# Configuration
PACKAGE_NAME="Brieflybot-lambda"
DEPLOYMENT_DIR="lambda-deployment"
PACKAGE_DIR="package"
ZIP_FILE="${PACKAGE_NAME}.zip"

# Clean up previous deployment
echo "🧹 Cleaning up previous deployment..."
rm -rf ${DEPLOYMENT_DIR}
rm -f ${ZIP_FILE}

# Create deployment directory
echo "📁 Creating deployment directory..."
mkdir -p ${DEPLOYMENT_DIR}
cd ${DEPLOYMENT_DIR}

# Create package directory for dependencies
echo "📦 Creating package directory..."
mkdir -p ${PACKAGE_DIR}

# Install dependencies
echo "⬇️ Installing dependencies..."
pip install --target ./${PACKAGE_DIR} -r ../requirements-lambda.txt

# Copy source code
echo "📋 Copying source code..."
cp ../lambda_function.py .
cp ../main.py .
cp -r ../slackbot .

# Create the zip file with dependencies at root
echo "🗜️ Creating deployment package..."
cd ${PACKAGE_DIR}
zip -r ../${ZIP_FILE} .

# Add source files to the zip
cd ..
zip ${ZIP_FILE} lambda_function.py main.py
zip -r ${ZIP_FILE} slackbot/

# Move zip file to project root
mv ${ZIP_FILE} ../

# Clean up
cd ..
rm -rf ${DEPLOYMENT_DIR}

echo "✅ Deployment package created: ${ZIP_FILE}"
echo "📊 Package size: $(du -h ${ZIP_FILE} | cut -f1)"
echo ""
echo "🚀 Ready to deploy to AWS Lambda!"
echo ""
echo "Next steps:"
echo "1. Upload ${ZIP_FILE} to AWS Lambda"
echo "2. Set handler to: lambda_function.lambda_handler"
echo "3. Configure environment variables"
echo "4. Set timeout to at least 5 minutes (300 seconds)"
echo "5. Set memory to at least 512 MB"
echo ""
echo "Environment variables needed:"
echo "- NEWSAPI_KEY (required)"
echo "- OPENAI_API_KEY or GEMINI_API_KEY (required)"
echo "- SLACK_BOT_TOKEN (required for publishing)"
echo "- SLACK_APP_TOKEN (required for publishing)"
echo "- SLACK_CHANNEL_ID (required for publishing)"
