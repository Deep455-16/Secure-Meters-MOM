# Production Deployment Guide

## Overview

This guide covers deploying the MOM Generator system to production, including setup, scaling, monitoring, and maintenance.

## Pre-Deployment Checklist

### System Requirements
- [ ] Windows Server 2016+ or Windows 10/11 Pro
- [ ] Python 3.8+ (or 3.10+ recommended)
- [ ] 8GB+ RAM (16GB+ recommended)
- [ ] 50GB+ free disk space
- [ ] Multi-core CPU (4+ cores recommended)
- [ ] GPU (optional, recommended for performance)

### Network Requirements
- [ ] Ollama server accessibility (HTTP port 11434)
- [ ] Network security (firewall rules)
- [ ] SSL/TLS for remote ollama (if applicable)
- [ ] DNS resolution

### Software Requirements
- [ ] Ollama installed and configured
- [ ] Python 3.8+
- [ ] Required Python packages installed
- [ ] File system permissions configured

---

## Installation

### 1. Environment Preparation

```powershell
# Create application directory
New-Item -ItemType Directory -Path "C:\MOMGenerator" -Force

# Navigate to directory
cd C:\MOMGenerator

# Copy all files from source
Copy-Item -Path "D:\Users\110778\Downloads\whisper.cpp_win_x64_v0.0.2\*" -Destination . -Recurse
```

### 2. Python Environment

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import requests; print('OK')"
```

### 3. Initial Configuration

```bash
# Run setup
python setup.py

# Verify deployment
python verify_deployment.py
```

### 4. Directory Permissions

```powershell
# Set folder permissions
$path = "C:\MOMGenerator"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "Everyone",
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)
$acl = Get-Acl $path
$acl.SetAccessRule($rule)
Set-Acl -Path $path -AclObject $acl
```

---

## Configuration

### Production config.json

```json
{
  "whisper_exe": "C:\\MOMGenerator\\main.exe",
  "whisper_model": "C:\\MOMGenerator\\models\\ggml-medium.bin",
  "ollama_url": "http://ollama-server:11434",
  "ollama_model": "llama2",
  "output_dir": "C:\\MOMGenerator",
  "recordings_dir": "C:\\MOMGenerator\\recordings",
  "transcripts_dir": "C:\\MOMGenerator\\transcripts",
  "moms_dir": "C:\\MOMGenerator\\moms",
  "timeout": 600,
  "retry_count": 3
}
```

### Environment Variables

```powershell
# Set environment variables
$env:OLLAMA_URL = "http://ollama-server:11434"
$env:OLLAMA_MODEL = "llama2"
$env:MOM_OUTPUT_DIR = "C:\MOMGenerator\moms"
$env:MOM_LOG_LEVEL = "INFO"

# Persist environment variables (PowerShell)
[Environment]::SetEnvironmentVariable("OLLAMA_URL", "http://ollama-server:11434", "Machine")
```

---

## Deployment Options

### Option 1: Windows Service

Create a Windows Service for automated processing:

```powershell
# Create service wrapper script
$serviceName = "MOMGeneratorService"
$binaryPath = "C:\MOMGenerator\mom_service.exe"

# (Requires Windows Service template - see below)
```

### Option 2: Scheduled Task

```powershell
# Create scheduled task for batch processing
$action = New-ScheduledTaskAction -Execute "C:\MOMGenerator\generate_mom_batch.bat" `
    -Argument "C:\MOMGenerator\recordings"

$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM

Register-ScheduledTask -TaskName "MOMGenerator" `
    -Action $action `
    -Trigger $trigger `
    -User "SYSTEM" `
    -RunLevel Highest
```

### Option 3: API Server

```python
# mom_api.py - REST API wrapper
from flask import Flask, request, jsonify
from mom_generator import MOMGenerator
import logging

app = Flask(__name__)
generator = MOMGenerator("config.json")
logging.basicConfig(level=logging.INFO)

@app.route('/generate-mom', methods=['POST'])
def generate_mom():
    """Generate MOM from audio file"""
    audio_file = request.files['audio'].filename
    request.files['audio'].save(audio_file)
    
    try:
        result = generator.process_meeting(audio_file)
        return jsonify({
            'status': 'success',
            'mom_file': result['mom_file'],
            'transcript_file': result['transcript_file']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

Deploy API:
```bash
pip install flask
python mom_api.py

# Or with production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 mom_api:app
```

---

## Performance Optimization

### CPU Optimization

```json
{
  "whisper_threads": 8,
  "ollama_threads": 4,
  "batch_size": 5
}
```

### GPU Acceleration

**Ollama GPU Support:**
```bash
# Configure ollama to use GPU
ollama serve --gpu auto

# Verify GPU usage
ollama list
```

**Whisper.cpp GPU (if available):**
- Requires CUDA toolkit
- Compile with GPU support
- Dramatically speeds up transcription

### Memory Optimization

```python
# Process large files in chunks
def process_large_audio(file_path, chunk_duration=600):
    """Process audio in 10-minute chunks"""
    # Implementation splits audio and processes sequentially
    pass
```

### I/O Optimization

```python
# Use SSD for recordings
# Use fast storage for transcripts
# Cache frequently accessed models
```

---

## Monitoring

### Logging Configuration

```python
# Enhanced logging in mom_generator.py
import logging
import logging.handlers

# File handler
file_handler = logging.handlers.RotatingFileHandler(
    'mom_generator.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

# Console handler
console_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Checks

```bash
# Regular health check script
python verify_deployment.py

# API health check (if using API)
curl http://localhost:5000/health
```

### Monitoring Metrics

Track:
- Processing time per file
- Queue depth
- Success/failure rate
- Error types
- System resource usage

```python
# Simple metrics collector
import time
from collections import defaultdict

class Metrics:
    def __init__(self):
        self.process_times = []
        self.errors = defaultdict(int)
        self.successes = 0
        
    def record_process(self, duration):
        self.process_times.append(duration)
        
    def record_error(self, error_type):
        self.errors[error_type] += 1
        
    def record_success(self):
        self.successes += 1
        
    def get_stats(self):
        return {
            'avg_time': sum(self.process_times) / len(self.process_times),
            'total_processed': self.successes,
            'error_count': sum(self.errors.values()),
            'errors_by_type': dict(self.errors)
        }
```

---

## Backup & Recovery

### Data Backup

```powershell
# Backup strategy
$backupPath = "\\backup\MOMGenerator\$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Backup transcripts and MOMs (not audio)
Copy-Item -Path "C:\MOMGenerator\transcripts" -Destination $backupPath -Recurse
Copy-Item -Path "C:\MOMGenerator\moms" -Destination $backupPath -Recurse
Copy-Item -Path "C:\MOMGenerator\config.json" -Destination $backupPath

# Backup database (if using database)
# sqlcmd -S SERVER -U user -P password -Q "BACKUP DATABASE MOMGenerator TO DISK='...'"
```

### Disaster Recovery

```powershell
# Restore from backup
$restorePath = "C:\MOMGenerator"
Copy-Item -Path "\\backup\MOMGenerator\*" -Destination $restorePath -Recurse -Force

# Verify restoration
python verify_deployment.py
```

---

## Scaling

### Horizontal Scaling

```python
# Process queue
from queue import Queue
import threading

class MOMProcessingQueue:
    def __init__(self, num_workers=4):
        self.queue = Queue()
        self.workers = []
        
        for i in range(num_workers):
            worker = threading.Thread(target=self.worker_loop)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def worker_loop(self):
        while True:
            audio_file = self.queue.get()
            try:
                generator.process_meeting(audio_file)
            except Exception as e:
                logging.error(f"Processing failed: {e}")
            finally:
                self.queue.task_done()
    
    def add_file(self, audio_file):
        self.queue.put(audio_file)
    
    def wait_completion(self):
        self.queue.join()
```

### Distributed Setup

```
Client A ──────┐
Client B ──────┤
Client C ──────├──> Load Balancer ──> MOM Worker Pool
Client D ──────┤                    (4+ instances)
Client E ──────┘
                        ↓
                  Shared Storage
                  (\\shared\input)
                        ↓
                   Ollama Server
                   (GPU-accelerated)
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Check error logs
- Verify processing queue

**Weekly:**
- Clean up processed files
- Verify backups
- Check disk space

**Monthly:**
- Update models
- Review performance metrics
- Security updates for Python/OS

**Quarterly:**
- Full backup verification
- Disaster recovery drill
- Performance optimization review

### Updates

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update Ollama models
ollama pull llama2
ollama pull neural-chat

# Update Whisper model (if needed)
# Download new model and update config.json
```

---

## Security

### Access Control

```powershell
# Restrict folder access
icacls "C:\MOMGenerator" /grant "DOMAIN\MOMGeneratorService:(OI)(CI)F"
icacls "C:\MOMGenerator" /remove "Users"
```

### Audio File Protection

```powershell
# Encrypt sensitive recordings
$file = "C:\MOMGenerator\recordings\sensitive.wav"
cipher /e /s:"C:\MOMGenerator\recordings"

# Set NTFS encryption
certutil -hide "C:\MOMGenerator\recordings\*"
```

### API Security (if using)

```python
from flask_httpauth import HTTPAuth
from werkzeug.security import check_password_hash

auth = HTTPAuth()

@auth.verify_password
def verify_password(username, password):
    users = {
        'admin': 'hashed_password_here'
    }
    return check_password_hash(users.get(username), password)

@app.route('/generate-mom', methods=['POST'])
@auth.login_required
def generate_mom():
    # Implementation
    pass
```

---

## Troubleshooting Production Issues

### Issue: "Out of Memory"

**Solution:**
```python
# Reduce batch size
# Process one file at a time
# Increase system RAM
# Enable virtual memory
```

### Issue: "Ollama Server Unavailable"

**Solution:**
```powershell
# Restart ollama
net stop ollama
net start ollama

# Or check if running
Get-Process ollama

# Or restart from config
ollama serve --reload
```

### Issue: "High Processing Times"

**Solution:**
```bash
# Check CPU/GPU usage
Get-Process

# Switch to faster model
# "ollama_model": "mistral"

# Use GPU acceleration
# Enable multi-threading

# Reduce output complexity
# Use simpler template
```

---

## Compliance & Auditing

### Logging for Compliance

```python
# Audit log
audit_log = logging.getLogger('audit')

audit_log.info(f"File processed: {filename}")
audit_log.info(f"MOM generated: {mom_file}")
audit_log.warning(f"Processing error: {error}")
```

### Data Retention

```powershell
# Implement retention policy
# Delete files older than 90 days
Get-ChildItem -Path "C:\MOMGenerator\recordings" -Recurse |
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-90)} |
    Remove-Item -Force
```

---

## Testing & Validation

### Pre-Deployment Testing

```bash
# Unit tests
python -m pytest tests/

# Integration tests
python tests/integration_test.py

# Load testing
# Generate 100 test files
# Process concurrently
# Monitor performance
```

### Production Validation

```powershell
# Process test meeting
.\generate_mom.bat test_meeting.wav

# Verify output quality
# Check MOM completeness
# Verify transcript accuracy

# Monitor system resources
# Check disk space
# Verify network connectivity
```

---

## Support Contacts

| Role | Contact |
|------|---------|
| Ollama Support | ollama.ai |
| Python Support | python.org |
| Windows Support | microsoft.com |
| Application Support | See README.md |

---

## Rollback Procedures

```powershell
# If deployment fails

# 1. Stop current service
Stop-Service -Name "MOMGeneratorService" -Force

# 2. Restore backup
$backupPath = "\\backup\MOMGenerator\latest"
Copy-Item -Path "$backupPath\*" -Destination "C:\MOMGenerator" -Recurse -Force

# 3. Restart service
Start-Service -Name "MOMGeneratorService"

# 4. Verify
python verify_deployment.py
```

---

## Performance Benchmarks

Expected performance on standard hardware:

| Task | Time | Notes |
|------|------|-------|
| Whisper transcription (30 min audio) | 5-10 min | CPU dependent |
| MOM generation | 1-2 min | Ollama model dependent |
| Total per meeting | 8-15 min | Sequential processing |
| Batch (10 meetings) | 1.5-2.5 hours | Sequential |

---

## Contact & Support

For deployment issues:
1. Check logs in `mom_generator.log`
2. Run `verify_deployment.py`
3. Review README.md troubleshooting
4. Check ARCHITECTURE.md for design details

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Status:** Production Ready
