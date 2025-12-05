#!/bin/bash
# Bash script to create/setup the virtual environment

# Detect if running on Cygwin
if command -v uname >/dev/null 2>&1; then
    if [ "$(uname -o 2>/dev/null)" = "Cygwin" ] || echo "$(uname -s 2>/dev/null)" | grep -qi cygwin; then
        VENV_DIR="venv-cygwin"
    else
        VENV_DIR="venv-unix"
    fi
else
    # Fallback: check for Cygwin-specific paths
    if [ -d "/cygdrive" ]; then
        VENV_DIR="venv-cygwin"
    else
        VENV_DIR="venv-unix"
    fi
fi

# Check if the virtual environment directory already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment '$VENV_DIR' already exists."
    echo "Checking if requirements are installed..."
    
    # Check if requirements are installed
    "$VENV_DIR/bin/pip" install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install requirements."
        exit 1
    fi
    
    echo "Requirements are up to date."
    exit 0
fi

echo "Creating virtual environment '$VENV_DIR'..."
python3 -m venv "$VENV_DIR"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

echo "Installing requirements..."
"$VENV_DIR/bin/pip" install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements."
    exit 1
fi

echo "Virtual environment created successfully!"
echo "You can now use './run.sh' to run the graph script."

