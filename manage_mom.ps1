# MOM Generator PowerShell Module
# Provides utility functions for managing the integration

param(
    [string]$Action = "help",
    [string]$AudioFile,
    [string]$OutputDir = ".",
    [string]$ConfigFile = "config.json"
)

function Test-OllamaServer {
    <#
    .SYNOPSIS
    Test connection to ollama server
    .EXAMPLE
    .\manage_mom.ps1 -Action test-ollama
    #>
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
        $models = $response.Content | ConvertFrom-Json
        Write-Host "✓ Ollama server is running" -ForegroundColor Green
        Write-Host "Available models:"
        $models.models | ForEach-Object { Write-Host "  - $($_.name)" }
        return $true
    }
    catch {
        Write-Host "✗ Cannot connect to ollama server" -ForegroundColor Red
        Write-Host "Make sure ollama is running at http://localhost:11434" -ForegroundColor Yellow
        return $false
    }
}

function Test-WhisperSetup {
    <#
    .SYNOPSIS
    Test whisper.cpp setup
    .EXAMPLE
    .\manage_mom.ps1 -Action test-whisper
    #>
    $config = Get-Content $ConfigFile | ConvertFrom-Json
    
    if (Test-Path $config.whisper_exe) {
        Write-Host "✓ Whisper executable found: $($config.whisper_exe)" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Whisper executable not found: $($config.whisper_exe)" -ForegroundColor Red
        return $false
    }
    
    if (Test-Path $config.whisper_model) {
        Write-Host "✓ Whisper model found: $($config.whisper_model)" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Whisper model not found: $($config.whisper_model)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

function Test-Environment {
    <#
    .SYNOPSIS
    Test complete setup (ollama + whisper)
    .EXAMPLE
    .\manage_mom.ps1 -Action test-env
    #>
    Write-Host "Testing MOM Generator Environment..." -ForegroundColor Cyan
    Write-Host ""
    
    $whistleOk = Test-WhisperSetup
    Write-Host ""
    $ollamaOk = Test-OllamaServer
    
    Write-Host ""
    if ($whistleOk -and $ollamaOk) {
        Write-Host "✓ All systems ready!" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "✗ Some components are missing or misconfigured" -ForegroundColor Red
        return $false
    }
}

function Process-AudioFile {
    <#
    .SYNOPSIS
    Process a single audio file
    .EXAMPLE
    .\manage_mom.ps1 -Action process -AudioFile "meeting.wav"
    #>
    param(
        [string]$File,
        [string]$OutDir
    )
    
    if (-not (Test-Path $File)) {
        Write-Host "✗ Audio file not found: $File" -ForegroundColor Red
        return
    }
    
    Write-Host "Processing: $File" -ForegroundColor Cyan
    python mom_generator.py --config $ConfigFile --audio $File --output $OutDir
}

function Process-BatchAudio {
    <#
    .SYNOPSIS
    Process all audio files in a directory
    .EXAMPLE
    .\manage_mom.ps1 -Action batch -AudioFile "recordings"
    #>
    param(
        [string]$Directory,
        [string]$OutDir
    )
    
    if (-not (Test-Path $Directory)) {
        Write-Host "✗ Directory not found: $Directory" -ForegroundColor Red
        return
    }
    
    Write-Host "Processing batch: $Directory" -ForegroundColor Cyan
    python mom_generator.py --config $ConfigFile --audio $Directory --batch --output $OutDir
}

function Show-Help {
    Write-Host "MOM Generator Management Tool" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\manage_mom.ps1 -Action <action> [parameters]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:"
    Write-Host "  help              Show this help message"
    Write-Host "  test-env          Test complete environment setup"
    Write-Host "  test-whisper      Test whisper.cpp setup"
    Write-Host "  test-ollama       Test ollama server connection"
    Write-Host "  process           Process single audio file"
    Write-Host "  batch             Process all files in directory"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\manage_mom.ps1 -Action test-env"
    Write-Host "  .\manage_mom.ps1 -Action process -AudioFile meeting.wav -OutputDir output"
    Write-Host "  .\manage_mom.ps1 -Action batch -AudioFile recordings -OutputDir output"
}

# Main execution
switch ($Action.ToLower()) {
    "test-env" { Test-Environment }
    "test-whisper" { Test-WhisperSetup }
    "test-ollama" { Test-OllamaServer }
    "process" { 
        if ($AudioFile) { 
            Process-AudioFile -File $AudioFile -OutDir $OutputDir 
        }
        else { 
            Write-Host "Error: -AudioFile parameter required" -ForegroundColor Red
        }
    }
    "batch" { 
        if ($AudioFile) { 
            Process-BatchAudio -Directory $AudioFile -OutDir $OutputDir 
        }
        else { 
            Write-Host "Error: -AudioFile parameter required" -ForegroundColor Red
        }
    }
    default { Show-Help }
}
