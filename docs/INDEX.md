# MOM Generator - Complete Integration Guide

## 📋 Table of Contents

1. **Quick Start** (5 minutes)
2. **Installation** (10 minutes)
3. **First Run** (15 minutes)
4. **Advanced Usage**
5. **Troubleshooting**
6. **API Reference**

---

## 🚀 Quick Start (First Time)

### Prerequisites
- Windows 10/11 (x64)
- Python 3.7+
- Ollama (https://ollama.ai)

### 3-Step Setup

**Step 1: Run Setup**
```batch
setup.bat
```
This will install dependencies and verify your system.

**Step 2: Start Ollama** (in a new terminal)
```batch
ollama serve
```

**Step 3: Generate MOM**
```batch
REM Single file:
generate_mom.bat recordings\meeting.wav

REM Or all files in a directory:
generate_mom_batch.bat recordings
```

✓ Done! Check the `moms/` folder for results.

---

## 📁 File Structure

```
whisper.cpp_win_x64_v0.0.2/
├── 🎯 START HERE
│   ├── QUICKSTART.md              ← First-time guide
│   ├── README.md                  ← Full documentation
│   ├── setup.bat                  ← One-time setup
│   └── verify_deployment.py       ← System check
│
├── 🎬 SCRIPTS (Easy to Use)
│   ├── generate_mom.bat           ← Process single audio file
│   ├── generate_mom_batch.bat     ← Process directory
│   ├── manage_mom.ps1             ← PowerShell tools
│   └── templates.bat              ← Template management
│
├── 🐍 PYTHON MODULES (Advanced)
│   ├── mom_generator.py           ← Main orchestrator
│   ├── mom_templates.py           ← Template system
│   ├── setup.py                   ← Setup automation
│   └── verify_deployment.py       ← Deployment verification
│
├── ⚙️ CONFIGURATION
│   ├── config.json                ← Settings
│   ├── mom_templates.json         ← Generated templates
│   └── requirements.txt           ← Python dependencies
│
├── 📚 DOCUMENTATION
│   ├── QUICKSTART.md              ← 5-minute setup
│   ├── README.md                  ← Complete reference
│   ├── TEMPLATES.md               ← Template customization
│   ├── ARCHITECTURE.md            ← System design
│   ├── INDEX.md                   ← This file
│   └── DEPLOYMENT.md              ← Production deployment
│
├── 📁 DATA DIRECTORIES
│   ├── recordings/                ← Input audio files
│   ├── transcripts/               ← Generated transcripts
│   ├── moms/                      ← Generated MOMs
│   └── models/                    ← Whisper model
│
├── 🔧 WHISPER.CPP
│   ├── main.exe                   ← Whisper executable
│   ├── whisper.dll                ← Whisper library
│   ├── stream/                    ← Streaming module
│   └── models/
│       └── ggml-medium.bin        ← Language model
│
└── 📄 THIS FILE
    └── INDEX.md                   ← Navigation guide
```

---

## 🎯 Quick Command Reference

### Basic Usage

```bash
# Setup (one time)
setup.bat

# Test system
python verify_deployment.py

# Process single file
generate_mom.bat path\to\meeting.wav

# Process directory
generate_mom_batch.bat path\to\recordings

# View MOMs
type moms\meeting_mom.txt
```

### PowerShell (Advanced)

```powershell
# Test environment
.\manage_mom.ps1 -Action test-env

# Process with options
.\manage_mom.ps1 -Action process -AudioFile meeting.wav -OutputDir custom_output

# Batch processing
.\manage_mom.ps1 -Action batch -AudioFile recordings
```

### Python (Developers)

```python
from mom_generator import MOMGenerator

generator = MOMGenerator("config.json")
result = generator.process_meeting("meeting.wav")
print(result['mom'])
```

---

## 📖 Documentation Guide

### For First-Time Users
→ Read **QUICKSTART.md**
- 5-minute setup
- Basic usage
- Troubleshooting tips

### For Full Reference
→ Read **README.md**
- Complete documentation
- All features
- Configuration options

### For Customization
→ Read **TEMPLATES.md**
- Customize MOM format
- Template examples
- Advanced prompts

### For Integration/Development
→ Read **ARCHITECTURE.md**
- System design
- Data flow
- API reference
- Integration points

### For Production Deployment
→ Read **DEPLOYMENT.md**
- Production checklist
- Performance tuning
- Monitoring
- Scaling

---

## 🔧 Common Tasks

### Task 1: Process a Single Meeting

```batch
generate_mom.bat C:\meetings\quarterly_review.wav
```

**Output:**
- `transcripts/quarterly_review.txt` - Full transcript
- `moms/quarterly_review_mom.txt` - Generated MOM

### Task 2: Process All Meetings in a Week

```batch
REM Copy all files to recordings folder
copy C:\meetings\week1\*.wav recordings\

REM Process all at once
generate_mom_batch.bat recordings
```

### Task 3: Customize MOM Format

```bash
# List available formats
templates.bat list

# Show a template
templates.bat show technical

# Generate with custom format
python mom_generator.py --audio meeting.wav --template technical
```

### Task 4: Check System Status

```bash
python verify_deployment.py
```

### Task 5: Use with PowerShell

```powershell
.\manage_mom.ps1 -Action test-env
.\manage_mom.ps1 -Action process -AudioFile meeting.wav
```

---

## 🎨 Template Options

Ready-to-use templates:

| Template | Best For | Speed |
|----------|----------|-------|
| **standard** | General meetings | Fast |
| **executive** | Leadership/summaries | Fast |
| **technical** | Engineering meetings | Medium |
| **agile** | Standups/sprints | Fast |
| **client** | Client meetings | Medium |
| **legal** | Compliance meetings | Slow |

### Using Templates

```bash
# Generate with specific template
python mom_generator.py --audio meeting.wav --template technical

# Create custom template
python mom_templates.py --add mytemplate "My Format" "Description" "Your prompt"

# List all templates
python mom_templates.py --list
```

---

## 🛠️ Configuration

### Main Config (config.json)

```json
{
  "whisper_exe": "main.exe",
  "whisper_model": "models/ggml-medium.bin",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama2",
  "output_dir": "."
}
```

### Change Settings

```json
{
  "ollama_model": "neural-chat"     // Switch to faster model
}
```

### Available Ollama Models

```bash
ollama pull llama2           # General purpose (default)
ollama pull neural-chat      # Conversation-optimized
ollama pull mistral          # Fast & efficient
ollama pull dolphin          # Creative content
ollama pull orca             # Advanced reasoning
```

---

## ⚡ Performance Tips

### Speed Up Processing

1. **Use smaller Ollama model**
   ```json
   { "ollama_model": "mistral" }  // Faster than llama2
   ```

2. **Process files sequentially** (default)
   ```batch
   generate_mom_batch.bat recordings
   ```

3. **Reduce template complexity**
   - Use "executive" instead of "technical"
   - Fewer output sections = faster

### Improve Quality

1. **Use larger model**
   ```bash
   ollama pull orca  // Better quality
   ```

2. **Improve audio quality**
   - Clear recording
   - Reduce background noise
   - Good microphone placement

3. **Use detailed template**
   - More specific prompts
   - Better structured output

---

## 🔍 Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| "Cannot connect to ollama" | Run: `ollama serve` |
| "Whisper not found" | Check main.exe exists |
| "No models on ollama" | Run: `ollama pull llama2` |
| Slow processing | Use faster model or GPU |
| Poor output | Improve audio quality |
| File not found | Check path and spelling |

See **README.md** for detailed troubleshooting.

---

## 🧪 Testing Your Setup

### Quick Test
```bash
python verify_deployment.py
```

### Full Test
```bash
setup.bat
.\manage_mom.ps1 -Action test-env
```

### Test with Sample
```batch
REM Use any audio file as test
generate_mom.bat sample_meeting.wav

REM Check if MOM was generated
type moms\sample_meeting_mom.txt
```

---

## 📚 Advanced Topics

### For Developers

- **Custom Integration**: ARCHITECTURE.md → "Integration Points"
- **API Usage**: See python examples in README.md
- **Template Development**: TEMPLATES.md → "Advanced"
- **Batch Processing**: See batch processing examples

### For DevOps

- **Scaling**: ARCHITECTURE.md → "Scaling Considerations"
- **Monitoring**: DEPLOYMENT.md → "Monitoring"
- **Distributed Setup**: ARCHITECTURE.md → "Advanced Setup"
- **Docker**: Can containerize with Dockerfile (see DEPLOYMENT.md)

### For Customization

- **Custom Prompts**: TEMPLATES.md → "Custom Templates"
- **Integrations**: ARCHITECTURE.md → "Integration"
- **Modified Workflow**: Edit mom_generator.py

---

## 🚀 Next Steps

### Immediate (Now)
1. ✓ Read QUICKSTART.md (5 min)
2. ✓ Run setup.bat
3. ✓ Test with sample audio

### Short Term (This Week)
- Process your first meeting
- Customize templates
- Integrate with your workflow

### Medium Term (This Month)
- Batch process all meetings
- Fine-tune templates
- Set up automatic scheduling

### Long Term (This Quarter)
- Integrate with email/Slack
- Archive MOM database
- Analyze meeting trends

---

## 📞 Support & Resources

### Built-In Help

```bash
# Setup help
python setup.py --help

# Generator help
python mom_generator.py --help

# Template help
python mom_templates.py --help

# Deployment verification
python verify_deployment.py --help
```

### Documentation

| Document | Purpose |
|----------|---------|
| QUICKSTART.md | Getting started fast |
| README.md | Complete reference |
| TEMPLATES.md | Customization guide |
| ARCHITECTURE.md | Technical design |
| DEPLOYMENT.md | Production setup |

### Common Issues

See **README.md** → "Troubleshooting" section

---

## 📋 Files Overview

### Scripts (Easy)
- `setup.bat` - Initial setup
- `generate_mom.bat` - Single file processing
- `generate_mom_batch.bat` - Batch processing
- `templates.bat` - Template management
- `manage_mom.ps1` - PowerShell tools

### Python Modules
- `mom_generator.py` - Main application (300+ lines)
- `mom_templates.py` - Template system (250+ lines)
- `setup.py` - Setup automation (200+ lines)
- `verify_deployment.py` - Verification tool (200+ lines)

### Configuration
- `config.json` - Main settings
- `requirements.txt` - Python dependencies
- `mom_templates.json` - Template definitions (auto-generated)

### Documentation
- `QUICKSTART.md` - 5-minute guide
- `README.md` - Complete manual
- `TEMPLATES.md` - Template guide
- `ARCHITECTURE.md` - Technical design
- `INDEX.md` - This file

---

## 🎓 Learning Path

**Beginner** (First time)
1. Read QUICKSTART.md
2. Run setup.bat
3. Process one meeting

**Intermediate** (Regular use)
1. Read README.md
2. Try different templates
3. Process meetings in batches

**Advanced** (Customization)
1. Read TEMPLATES.md & ARCHITECTURE.md
2. Create custom templates
3. Modify python scripts
4. Integrate with other systems

**Expert** (Production)
1. Read DEPLOYMENT.md
2. Set up monitoring
3. Scale to multiple servers
4. Optimize for your workflow

---

## ✅ Checklist: Ready to Use

- [ ] Python 3.7+ installed
- [ ] Ollama installed and running
- [ ] setup.bat completed
- [ ] verify_deployment.py passed
- [ ] Audio files in recordings/ folder
- [ ] First MOM generated successfully
- [ ] Templates customized (optional)

---

## 🔗 Related Files

- System Design: `ARCHITECTURE.md`
- Full Docs: `README.md`
- Setup Guide: `QUICKSTART.md`
- Templates: `TEMPLATES.md`
- Production: `DEPLOYMENT.md`

---

**Start here:** Open **QUICKSTART.md** for 5-minute setup, or **README.md** for comprehensive documentation.

**Questions?** Check **README.md** → Troubleshooting section.

**Ready?** Run `setup.bat` now!
