#!/usr/bin/env pwsh
# Windows equivalent of start.sh. Run from PowerShell:  .\start.ps1
$ErrorActionPreference = 'Stop'

$nlpSuiteDir = if ($env:NLP_SUITE_DIR) { $env:NLP_SUITE_DIR } else { Join-Path $HOME 'nlp-suite' }

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Docker is not running. Please start Docker Desktop and try again.'
    exit 1
}

foreach ($sub in 'input', 'output', 'csvInput') {
    New-Item -ItemType Directory -Force -Path (Join-Path $nlpSuiteDir $sub) | Out-Null
}

$env:NLP_SUITE_DIR = $nlpSuiteDir

docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host 'docker compose failed to start the services.'
    exit 1
}

Write-Host 'Waiting for NLP Suite to start...'
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        Invoke-WebRequest -Uri 'http://localhost:8000' -UseBasicParsing -TimeoutSec 2 *> $null
        $ready = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host 'NLP Suite did not start within 60 seconds.'
    Write-Host "Run 'docker compose logs' to investigate."
    exit 1
}

Write-Host 'NLP Suite is running at http://localhost:8000'
Write-Host "Your files are at: $nlpSuiteDir"

Start-Process 'http://localhost:8000'
