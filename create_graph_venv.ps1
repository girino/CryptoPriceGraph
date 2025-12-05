# PowerShell script to create/setup the virtual environment

$VENV_DIR = "venv"

# Check if the virtual environment directory already exists
if (Test-Path $VENV_DIR) {
    Write-Host "Virtual environment '$VENV_DIR' already exists."
    Write-Host "Checking if requirements are installed..."
    
    # Check if requirements are installed
    & "$VENV_DIR\Scripts\pip.exe" install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install requirements." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Requirements are up to date." -ForegroundColor Green
    exit 0
}

Write-Host "Creating virtual environment '$VENV_DIR'..."
python -m venv $VENV_DIR

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to create virtual environment." -ForegroundColor Red
    exit 1
}

Write-Host "Installing requirements..."
& "$VENV_DIR\Scripts\pip.exe" install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install requirements." -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment created successfully!" -ForegroundColor Green
Write-Host "You can now use 'run_graph.ps1' to run the graph script."

