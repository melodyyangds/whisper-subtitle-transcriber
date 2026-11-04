param(
    [string]$MediaPath = '',
    [ValidateSet('small','medium')][string]$Model = 'small',
    [switch]$SetupOnly
)
$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $scriptDir '.venv\Scripts\python.exe'
$requirements = Join-Path $scriptDir 'requirements.txt'

function Find-Python {
    $py = Get-Command 'py.exe' -ErrorAction SilentlyContinue
    if ($py) {
        foreach ($version in @('-3.12', '-3.11', '-3.10')) {
            try {
                & $py.Source $version -c 'import sys; assert (3, 10) <= sys.version_info[:2] <= (3, 12)' 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) { return ,@($py.Source, $version) }
            } catch { }
        }
    }
    $candidate = Get-Command 'python.exe' -ErrorAction SilentlyContinue
    if ($candidate) {
        try {
            & $candidate.Source -c 'import sys; assert (3, 10) <= sys.version_info[:2] <= (3, 12)' 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { return ,@($candidate.Source) }
        } catch { }
    }
    return $null
}

function Ensure-Python {
    if (Test-Path -LiteralPath $venvPython -PathType Leaf) { return }
    Write-Host 'First-time setup: checking for Python 3.10 to 3.12...'
    $python = Find-Python
    if (-not $python) {
        Write-Host 'Python not found. Attempting to install Python 3.12 through Windows Package Manager...'
        $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
        if (-not $winget) {
            throw 'Please install Python 3.12 from python.org (enable Add python.exe to PATH), then run this BAT again.'
        }
        & $winget.Source install --id Python.Python.3.12 --exact --source winget --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) { throw 'Python installation did not finish. Install Python 3.12 manually, then retry.' }
        $installedPath = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
        if (Test-Path -LiteralPath $installedPath) { $python = @($installedPath) }
        else { $python = Find-Python }
        if (-not $python) { throw 'Python installed but could not be found. Restart the launcher, or install Python 3.12 from python.org.' }
    }
    Write-Host 'Creating the private .venv environment...'
    if ($python.Count -eq 2) { & $python[0] $python[1] -m venv (Join-Path $scriptDir '.venv') }
    else { & $python[0] -m venv (Join-Path $scriptDir '.venv') }
    if ($LASTEXITCODE -ne 0) { throw 'Unable to create Python virtual environment.' }
}

function Ensure-Packages {
    # Call an actual .py file, not python -c with nested quotes.
    # Windows PowerShell 5.1 can strip inner quotes in native-command arguments.
    $verifyScript = Join-Path $scriptDir 'verify_install.py'
    $healthy = $false
    try {
        & $venvPython $verifyScript 2>$null | Out-Null
        $healthy = ($LASTEXITCODE -eq 0)
    } catch { $healthy = $false }
    if ($healthy) {
        Write-Host 'Packages already installed and verified; skipping installation.' -ForegroundColor Green
        return
    }
    Write-Host 'Installing free transcription software into .venv (requires internet on first run)...'
    & $venvPython -m pip install --disable-pip-version-check -r $requirements
    if ($LASTEXITCODE -ne 0) { throw 'Package installation failed. Check your internet connection and try again.' }
    & $venvPython $verifyScript
    if ($LASTEXITCODE -ne 0) { throw 'Package verification failed. See the error above; no need to delete .venv for the earlier quoting error.' }
}

try {
    Ensure-Python
    Ensure-Packages
    if ($SetupOnly) {
        Write-Host 'Setup complete. Drag an audio/video file onto either BAT to transcribe.' -ForegroundColor Green
        exit 0
    }
    if (-not $MediaPath) {
        Add-Type -AssemblyName System.Windows.Forms
        $picker = New-Object System.Windows.Forms.OpenFileDialog
        $picker.Title = 'Choose an audio or video file to transcribe'
        $picker.Filter = 'Audio and video (*.m4a;*.mp3;*.wav;*.mp4;*.mov;*.mkv;*.flac;*.ogg;*.webm;*.aac;*.wma)|*.m4a;*.mp3;*.wav;*.mp4;*.mov;*.mkv;*.flac;*.ogg;*.webm;*.aac;*.wma|All files (*.*)|*.*'
        if ($picker.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
            Write-Host 'No file selected. Nothing was changed.'
            exit 0
        }
        $MediaPath = $picker.FileName
    }
    if (-not (Test-Path -LiteralPath $MediaPath -PathType Leaf)) { throw "File not found: $MediaPath" }
    Write-Host "Selected model: $Model (CPU mode, no paid API)"
    & $venvPython (Join-Path $scriptDir 'transcribe.py') $MediaPath --model $Model --language zh --chinese traditional
    if ($LASTEXITCODE -ne 0) { throw 'Transcription failed. The error above may explain why.' }
    Write-Host 'Done! TXT and SRT files were saved beside your original media.' -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
