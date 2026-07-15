# 🚀 START LOCALHOST - QUICK GUIDE

## Run on Localhost in 2 Steps

### Step 1️⃣: Install Dependencies
```bash
pip install flask flask-cors
```

### Step 2️⃣: Start Services

**Option A: Automatic (Easiest)**
```bash
start_localhost.bat
```
Starts Ollama + API server automatically.

**Option B: Manual (2 Terminals)**

Terminal 1:
```bash
ollama serve
```

Terminal 2:
```bash
start_server.bat
```

---

## 🌐 Access

**Web Interface:** http://localhost:5000

**API Endpoint:** http://localhost:5000/api/v1/

---

## ✨ Features

### Web UI
1. Upload audio files
2. Choose MOM template
3. Generate automatically
4. View results instantly

### REST API
- Generate MOM from audio
- Transcribe only
- Generate from text
- Download files
- Check status

### Templates
- Standard (full MOM)
- Executive (summary)
- Technical (engineering)
- Agile (standups)
- Client (professional)
- Legal (formal)

---

## 📋 What Happens

```
1. Upload audio file
   ↓
2. Whisper.cpp transcribes
   ↓
3. Ollama LLM generates MOM
   ↓
4. Results shown in browser
```

---

## 🔗 Example URLs

Open these in your browser:

- Web UI: http://localhost:5000/
- Status: http://localhost:5000/api/v1/status
- Models: http://localhost:5000/api/v1/models
- Templates: http://localhost:5000/api/v1/templates
- Files: http://localhost:5000/api/v1/files

---

## 🛠️ Command Reference

```bash
# Check server is running
curl http://localhost:5000/health

# Get system status
curl http://localhost:5000/api/v1/status

# Upload and generate (PowerShell)
$file = Get-Item meeting.wav
Invoke-WebRequest -Uri "http://localhost:5000/api/v1/generate" `
  -Method Post `
  -Form @{audio=$file; template='standard'} `
  -OutFile result.json
```

---

## ⚡ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect" | Run `ollama serve` first |
| "Port in use" | Kill process on 5000 or use different port |
| "Module not found" | Run `pip install flask flask-cors` |
| "File not found" | Check setup.bat was run |

---

## 📚 Full Documentation

See **LOCALHOST.md** for:
- Complete API reference
- Code examples
- Integration guides
- Security setup
- Production deployment

---

**Ready?** Run `start_server.bat` now! 🎉

## Keyboard Shortcuts

- `Ctrl+C` - Stop server
- `Ctrl+L` - Clear browser cache
- `F5` - Refresh page

---

**Status:** ✅ Ready to run on localhost
