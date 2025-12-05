#!/bin/bash
# Bash script to run graph.py from the virtual environment

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

SCRIPT="graph.py"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment '$VENV_DIR' does not exist."
    echo "Please run './create_venv.sh' first to create it."
    exit 1
fi

# Check if graph.py exists
if [ ! -f "$SCRIPT" ]; then
    echo "Error: '$SCRIPT' not found in current directory."
    exit 1
fi

# Activate the virtual environment and run the script
echo "Activating virtual environment and running $SCRIPT..."
source "$VENV_DIR/bin/activate"

# Run graph.py with all passed arguments
python "$SCRIPT" "$@"

# Store exit code before deactivating
EXIT_CODE=$?

# Deactivate the virtual environment
deactivate

exit $EXIT_CODE

