# PowerShell script to run graph.py from the virtual environment

$VENV_DIR = "venv-windows"
$SCRIPT = "graph.py"

# Check if virtual environment exists
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "Virtual environment '$VENV_DIR' does not exist." -ForegroundColor Red
    Write-Host "Please run 'create_venv.ps1' first to create it." -ForegroundColor Yellow
    exit 1
}

# Check if graph.py exists
if (-not (Test-Path $SCRIPT)) {
    Write-Host "Error: '$SCRIPT' not found in current directory." -ForegroundColor Red
    exit 1
}

# Activate the virtual environment and run the script
Write-Host "Activating virtual environment and running $SCRIPT..." -ForegroundColor Cyan
& "$VENV_DIR\Scripts\Activate.ps1"

# Run graph.py with all passed arguments
& python $SCRIPT $args

# Deactivate the virtual environment
deactivate

