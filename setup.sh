#!/bin/bash

# Exit immediately on errors
set -e

# Define venv path
VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    echo "✅ Virtual environment already exists. Activating..."
    echo "🔁 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo "🆕 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created."

    echo "🔁 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"

    if ! pip show hipotech_analysis &>/dev/null; then
        echo "📦 Installing wheel package..."
        pip install dist/hipotech_analysis-0.2.0-py3-none-any.whl
    else
        echo "✅ hipotech_analysis wheel already installed."
    fi

    echo "📦 Installing Python requirements..."
    pip install -r requirements.txt

    echo "🌐 Installing Playwright browsers..."
    playwright install
fi

# === AWS CONFIGURATION CHECK ===

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials file exists and contains credentials
AWS_CREDENTIALS_FILE="$HOME/.aws/credentials"

if [ ! -f "$AWS_CREDENTIALS_FILE" ] || ! grep -q "aws_access_key_id" "$AWS_CREDENTIALS_FILE"; then
    echo "🆕 AWS credentials not found or incomplete."
    echo "🔐 Running 'aws configure' to set them up..."
    aws configure
else
    echo "✅ AWS credentials already configured."
fi

echo "🚀 Running the Streamlit app..."
streamlit run app.py
