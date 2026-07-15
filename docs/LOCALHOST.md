# Running MOM Generator on Localhost

## Overview

The MOM Generator now includes a **REST API server** that runs on **localhost:5000** with a built-in web interface.

---

## ⚡ Quick Start (3 Commands)

### Terminal 1: Setup
```bash
setup.bat
pip install flask flask-cors
```

### Terminal 2: Start Ollama
```bash
ollama serve
```

### Terminal 3: Start API Server
```bash
start_server.bat
```

Then open your browser to: **http://localhost:5000**

---

## 🚀 Startup Options

### Option 1: Simple (Windows Batch)

**One Command - Starts Ollama + API Server:**
```bash
start_localhost.bat
```
Opens Ollama and API server automatically.

**Or separately:**
```bash
REM Terminal 1
ollama serve

REM Terminal 2
start_server.bat
```

### Option 2: PowerShell

```powershell
# Terminal 1
ollama serve

# Terminal 2
.\start_server.ps1
```

### Option 3: Command Line

```bash
python mom_api_server.py
```

---

## 🌐 Web Interface

### Access URL
```
http://localhost:5000
```

### Features
1. **Upload Audio & Generate MOM**
   - Select audio file
   - Choose template
   - Click "Generate MOM"
   - View results

2. **Generate MOM from Text**
   - Paste transcript
   - Choose template
   - Click "Generate"
   - View formatted MOM

3. **System Status**
   - Shows Ollama connection
   - Shows Whisper status
   - Shows available models

---

## 📡 REST API Endpoints

### Health & Status

**Check Server Health:**
```bash
curl http://localhost:5000/health
```

**Get System Status:**
```bash
curl http://localhost:5000/api/v1/status
```

**List Available Models:**
```bash
curl http://localhost:5000/api/v1/models
```

**List Templates:**
```bash
curl http://localhost:5000/api/v1/templates
```

### Generate MOM

**Upload Audio File:**
```bash
curl -X POST \
  -F "audio=@meeting.wav" \
  -F "template=standard" \
  http://localhost:5000/api/v1/generate
```

**Generate from Text:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Your meeting transcript here...",
    "template": "standard"
  }' \
  http://localhost:5000/api/v1/generate-from-text
```

**Transcribe Only (No MOM):**
```bash
curl -X POST \
  -F "audio=@meeting.wav" \
  http://localhost:5000/api/v1/transcribe
```

### File Management

**List Generated Files:**
```bash
curl http://localhost:5000/api/v1/files
```

**Download Transcript:**
```bash
curl http://localhost:5000/api/v1/download/transcript/meeting.txt -o meeting.txt
```

**Download MOM:**
```bash
curl http://localhost:5000/api/v1/download/mom/meeting_mom.txt -o meeting_mom.txt
```

---

## 🛠️ Python Client Example

```python
import requests
import json

# Configuration
API_URL = "http://localhost:5000"

# Check status
response = requests.get(f"{API_URL}/api/v1/status")
print(json.dumps(response.json(), indent=2))

# Generate MOM from audio
files = {'audio': open('meeting.wav', 'rb')}
data = {'template': 'standard'}
response = requests.post(f"{API_URL}/api/v1/generate", files=files, data=data)
result = response.json()
print("Generated MOM:")
print(result['mom'])

# Generate from text
payload = {
    'transcript': 'Meeting transcript here...',
    'template': 'executive'
}
response = requests.post(
    f"{API_URL}/api/v1/generate-from-text",
    json=payload
)
result = response.json()
print(result['mom'])
```

---

## 🐚 Bash/Shell Script Example

```bash
#!/bin/bash

API_URL="http://localhost:5000"

# Check status
echo "Checking system status..."
curl -s $API_URL/api/v1/status | jq .

# Generate MOM from audio file
echo "Generating MOM from audio..."
curl -s -X POST \
  -F "audio=@/path/to/meeting.wav" \
  -F "template=technical" \
  $API_URL/api/v1/generate | jq '.mom'

# List all files
echo "List generated files..."
curl -s $API_URL/api/v1/files | jq .
```

---

## 📋 JavaScript/Fetch Example

```javascript
// Check server status
fetch('http://localhost:5000/api/v1/status')
  .then(r => r.json())
  .then(data => console.log('System Status:', data));

// Upload audio and generate MOM
const formData = new FormData();
formData.append('audio', audioFileElement.files[0]);
formData.append('template', 'standard');

fetch('http://localhost:5000/api/v1/generate', {
  method: 'POST',
  body: formData
})
.then(r => r.json())
.then(data => console.log('Generated MOM:', data.mom));

// Generate from text
fetch('http://localhost:5000/api/v1/generate-from-text', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    transcript: 'Your transcript...',
    template: 'executive'
  })
})
.then(r => r.json())
.then(data => console.log('MOM:', data.mom));
```

---

## 📱 Integrations

### Postman

1. Import the following collection:

```json
{
  "info": {"name": "MOM Generator API"},
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/health"
      }
    },
    {
      "name": "Generate MOM",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/v1/generate",
        "body": {
          "mode": "formdata",
          "formdata": [
            {"key": "audio", "type": "file"},
            {"key": "template", "value": "standard"}
          ]
        }
      }
    }
  ]
}
```

### Excel/Google Sheets

Use `=IMPORTXML()` or similar functions to call the API.

### Webhook Integration

```bash
# Send MOM to Slack webhook
TRANSCRIPT="Meeting transcript..."
MOM=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"transcript\": \"$TRANSCRIPT\", \"template\": \"standard\"}" \
  http://localhost:5000/api/v1/generate-from-text | jq -r '.mom')

curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\": \"Generated MOM:\n$MOM\"}" \
  $SLACK_WEBHOOK_URL
```

---

## ⚙️ Configuration

### Environment Variables

```powershell
# Set Ollama URL
$env:OLLAMA_URL = "http://localhost:11434"

# Set Ollama model
$env:OLLAMA_MODEL = "llama2"

# Set Flask debug (development only)
$env:FLASK_DEBUG = 0
```

### API Server Config

Edit `config.json`:
```json
{
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama2",
  "whisper_model": "models/ggml-medium.bin"
}
```

---

## 🔐 Security Notes

### Local Development
- Current setup is for **local use only**
- No authentication required for localhost

### Production Deployment
For production on accessible networks, add:

1. **Authentication:**
```python
from flask_httpauth import HTTPAuth

auth = HTTPAuth()

@auth.verify_password
def verify(username, password):
    # Your auth logic
    pass

@app.route('/api/v1/generate', methods=['POST'])
@auth.login_required
def generate_mom():
    # Your code
    pass
```

2. **SSL/TLS:**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run with SSL
python mom_api_server.py --ssl
```

3. **Rate Limiting:**
```python
from flask_limiter import Limiter

limiter = Limiter(app)

@app.route('/api/v1/generate', methods=['POST'])
@limiter.limit("5/minute")
def generate_mom():
    pass
```

---

## 🐛 Troubleshooting

### "Address already in use"
```bash
# Port 5000 is already in use
# Kill the process or use different port
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### "Cannot connect to Ollama"
```bash
# Make sure Ollama is running
ollama serve

# Or check if it's on a different port
netstat -an | findstr 11434
```

### "Module not found (flask)"
```bash
# Install Flask
pip install flask flask-cors
```

### "Permission denied"
```bash
# Windows: Run as Administrator
# Or use different port (> 1024)
```

---

## 📊 Performance

### Localhost Performance
- **Latency:** < 1ms (local calls)
- **Throughput:** Depends on Ollama and Whisper performance
- **Concurrency:** Flask supports multiple requests

### Optimization

```python
# For production, use WSGI server:
pip install gunicorn
gunicorn -w 4 -b localhost:5000 mom_api_server:app
```

---

## 🚀 Deployment Options

### Docker

```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "mom_api_server.py"]
```

Run:
```bash
docker build -t mom-generator .
docker run -p 5000:5000 -p 11434:11434 mom-generator
```

### Systemd (Linux)

```ini
[Unit]
Description=MOM Generator API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mom-generator
ExecStart=/usr/bin/python3 mom_api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Windows Service

Use `nssm` (Non-Sucking Service Manager):
```bash
nssm install MOMGenerator "C:\path\to\python.exe" "C:\path\to\mom_api_server.py"
nssm start MOMGenerator
```

---

## 📝 API Response Format

### Success Response
```json
{
  "status": "success",
  "filename": "meeting.wav",
  "template": "standard",
  "transcript": "Full transcript...",
  "mom": "Generated MOM content...",
  "files": {
    "transcript": "transcripts/meeting.txt",
    "mom": "moms/meeting_mom.txt"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Description of error",
  "type": "ErrorType"
}
```

---

## 🎯 Common Use Cases

### Case 1: Batch Processing
```bash
for file in meetings/*.wav; do
  curl -X POST \
    -F "audio=@$file" \
    -F "template=technical" \
    http://localhost:5000/api/v1/generate \
    -o "moms/$(basename $file .wav)_mom.txt"
done
```

### Case 2: Real-time Transcription Dashboard
- Host web UI at localhost:5000
- Real-time upload and processing
- Download results directly

### Case 3: Integration with CMS
```python
# WordPress/Drupal plugin
response = requests.post('http://localhost:5000/api/v1/generate', 
                        files={'audio': audio_file},
                        data={'template': 'client'})
mom = response.json()['mom']
# Store in CMS
```

---

## 📞 Support

For issues:
1. Check logs in terminal
2. Run `python verify_deployment.py`
3. See README.md Troubleshooting
4. Check http://localhost:5000/api/v1/status for system status

---

**Ready to start?** Run `start_server.bat` now! 🚀
