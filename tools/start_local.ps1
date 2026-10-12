param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$url = 'http://127.0.0.1:8765/'

function Test-Chill {
    try {
        $page = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
        return ($page.StatusCode -eq 200 -and $page.Content -match 'data-nav="practice"' -and $page.Content -match '/app.js')
    } catch { return $false }
}

try {
    if (-not (Test-Chill)) {
        # Do not stop another application that owns this port.
        $probe = [System.Net.Sockets.TcpClient]::new()
        try {
            $connection = $probe.ConnectAsync('127.0.0.1', 8765)
            $occupied = $connection.Wait(1000) -and $probe.Connected
        } catch { $occupied = $false } finally { $probe.Dispose() }
        if ($occupied) { throw 'Port 8765 is occupied or Co Chill is not responding. Do not start a second server. Retry shortly or inspect the running server.' }

        $pythonExe = $null
        foreach ($candidate in @('python', 'py')) {
            $command = Get-Command $candidate -ErrorAction SilentlyContinue
            if ($command) {
                $resolved = & $command.Source -c "import sys; assert sys.version_info >= (3,10); print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0 -and $resolved -and (Test-Path -LiteralPath ([string]$resolved))) {
                    $pythonExe = [string]$resolved
                    break
                }
            }
        }
        if (-not $pythonExe) { throw 'Python 3.10+ is required. Install Python, then double-click Mo_Co_Chill.cmd again.' }
        $logDir = Join-Path $projectRoot 'var'
        New-Item -ItemType Directory -Force -Path $logDir | Out-Null
        $serverPath = Join-Path $projectRoot 'server.py'
        $process = Start-Process -FilePath $pythonExe -ArgumentList @('-u', ('"' + $serverPath + '"'), '--port', '8765') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir 'server-output.log') -RedirectStandardError (Join-Path $logDir 'server-error.log') -PassThru
        $ready = $false
        for ($attempt = 0; $attempt -lt 15; $attempt++) {
            if (Test-Chill) { $ready = $true; break }
            if ($process.HasExited) { break }
            Start-Sleep -Milliseconds 400
        }
        if (-not $ready) { throw 'Server did not become ready. See var\server-error.log and var\server-output.log.' }
        Write-Host 'Co Chill started in the background.'
    } else {
        Write-Host 'Co Chill is already running; reusing the existing server.'
    }
    Write-Host $url
    if (-not $NoBrowser) { Start-Process $url }
    exit 0
} catch {
    Write-Host ('Cannot open Co Chill: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
