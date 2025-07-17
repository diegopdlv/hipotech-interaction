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

    # Check if dependencies are already installed (optional but useful speed boost)
    if ! pip show hipotech_analysis &>/dev/null; then
        echo "📦 Installing wheel package..."
        pip install dist/hipotech_analysis-0.1.0-py3-none-any.whl
    else
        echo "✅ hipotech_analysis wheel already installed."
    fi

    echo "📦 Installing Python requirements..."
    pip install -r requirements.txt

    echo "🌐 Installing Playwright browsers..."
    playwright install

fi

echo "🚀 Running the Streamlit app..."
streamlit run app.py
