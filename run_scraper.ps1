# =================================================================
#  PowerShell script to automatically restart the Python crawler
#  Function: If python get_backer_city_state.py stops running,
#            this script will wait for 5 minutes and then automatically restart it.
# =================================================================

while ($true) {
    $currentTime = Get-Date -Format "HH:mm:ss.ff"
    Write-Host "[$currentTime] Preparing to activate conda environment and start Python program..."

    # Attempt to activate the conda environment.
    conda activate ".\.venv"

    if ($LASTEXITCODE -ne 0) {
        $currentTime = Get-Date -Format "HH:mm:ss.ff"
        Write-Host "[$currentTime] Failed to activate conda environment. Please check your conda installation and environment path."
    } else {
        $currentTime = Get-Date -Format "HH:mm:ss.ff"
        Write-Host "[$currentTime] Conda environment activated. Starting Python program: get_backer_city_state.py"

        # Execute your Python program
        python get_backer_city_state.py
    }

    $currentTime = Get-Date -Format "HH:mm:ss.ff"
    Write-Host ""
    Write-Host "[$currentTime] Python program has stopped."
    Write-Host "Waiting for 5 minutes before automatically restarting..."
    Write-Host "To completely terminate this auto-restart loop, close this window or press Ctrl+C."
    Write-Host ""

    # Wait for 300 seconds (5 minutes)
    Start-Sleep -Seconds 300

    $currentTime = Get-Date -Format "HH:mm:ss.ff"
    Write-Host "[$currentTime] Restarting the process..."
    Write-Host ""

    # Deactivate the conda environment (optional)
    conda deactivate
}
