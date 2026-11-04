param([Parameter(Mandatory=$true)][string]$MediaPath)
$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $scriptDir '.venv\Scripts\python.exe'
try {
    if (-not (Test-Path -LiteralPath $MediaPath -PathType Leaf)) { throw "File not found: $MediaPath" }
    if (-not (Test-Path -LiteralPath $venvPython)) {
        Write-Host 'First-run setup: finding Python 3.10-3.12...'
        $python = $null
        if (Get-Command py -ErrorAction SilentlyContinue) {
            foreach ($ver in @('-3.12', '-3.11', '-3.10')) {
                # The Windows py launcher can throw "No suitable Python runtime found".
                # That only means this particular version is absent: continue probing.
                try {
                    & py $ver -c "import sys" 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) { $python = @('py', $ver); break }
                } catch { continue }
            }
        }
        if (-not $python -and (Get-Command python -ErrorAction SilentlyContinue)) {
            try {
                & python -c "import sys; assert (3, 10) <= sys.version_info[:2] <= (3, 12)" 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) { $python = @('python') }
            } catch { }
        }
        if (-not $python) {
            Write-Host 'Python not found. Installing Python 3.12 with Windows Package Manager...'
            if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'winget unavailable. Install Python 3.12 from python.org, then try again.' }
            & winget install --id Python.Python.3.12 --exact --source winget --accept-package-agreements --accept-source-agreements
            if ($LASTEXITCODE -ne 0) { throw 'Python installation failed or was cancelled.' }
            $pyPath = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
            if (Test-Path $pyPath) { $python = @($pyPath) }
            elseif (Get-Command py -ErrorAction SilentlyContinue) { $python = @('py', '-3.12') }
            else { throw 'Python installed, but not found. Close and reopen this tool.' }
        }
        Write-Host 'Creating private Python environment...'
        if ($python.Count -eq 2) { & $python[0] $python[1] -m venv (Join-Path $scriptDir '.venv') }
        else { & $python[0] -m venv (Join-Path $scriptDir '.venv') }
        if ($LASTEXITCODE -ne 0) { throw 'Could not create Python environment.' }
        Write-Host 'Installing free transcription engine (first time only)...'
        & $venvPython -m pip install --disable-pip-version-check 'faster-whisper==1.2.1' 'av>=11,<19'
        if ($LASTEXITCODE -ne 0) { throw 'Could not install faster-whisper.' }
    }
    # Repair environments installed by older versions of this launcher:
    # faster-whisper 1.2.1 passes metadata_errors, which PyAV 19 removed.
    $avMajor = & $venvPython -c "import av; print(av.__version__.split('.')[0])"
    if ($LASTEXITCODE -ne 0) { throw 'Unable to check PyAV version.' }
    if ([int]$avMajor -ge 19) {
        Write-Host 'Fixing incompatible PyAV 19 installation (one-time)...'
        & $venvPython -m pip install --disable-pip-version-check 'av>=11,<19'
        if ($LASTEXITCODE -ne 0) { throw 'Could not install compatible PyAV.' }
    }
    & $venvPython (Join-Path $scriptDir 'transcribe.py') $MediaPath
    if ($LASTEXITCODE -ne 0) { throw 'Transcription failed. See the error above.' }
    Write-Host 'Done! Output files are beside your video.' -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
