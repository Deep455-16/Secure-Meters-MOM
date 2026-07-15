# 🎯 QUICK REFERENCE CARD

## MOM Generator - Whisper.cpp + Ollama Integration

**Location:** `d:\Users\110778\Downloads\whisper.cpp_win_x64_v0.0.2\`

---

## ⚡ QUICK COMMANDS

```bash
# Setup (once)
setup.bat

# Test system
python verify_deployment.py

# Process single file
generate_mom.bat meeting.wav

# Process directory
generate_mom_batch.bat recordings

# View templates
templates.bat list

# PowerShell tools
.\manage_mom.ps1 -Action test-env
```

---

## 📚 READ FIRST

1. **START_HERE.md** ← You are here
2. **QUICKSTART.md** ← 5-minute guide
3. **README.md** ← Full manual

---

## 🎨 TEMPLATES

```bash
# Standard - Full MOM (default)
python mom_generator.py --audio meeting.wav

# Executive - Brief summary
python mom_generator.py --audio meeting.wav --template executive

# Technical - Engineering focus
python mom_generator.py --audio meeting.wav --template technical

# Agile - Standup format
python mom_generator.py --audio meeting.wav --template agile

# Client - Professional tone
python mom_generator.py --audio meeting.wav --template client

# Legal - Formal format
python mom_generator.py --audio meeting.wav --template legal
```

---

## 📁 FOLDER LAYOUT

| Folder | Purpose |
|--------|---------|
| `recordings/` | Put audio files here |
| `transcripts/` | Generated transcripts (auto) |
| `moms/` | Generated MOMs (auto) |
| `models/` | Whisper model (ggml-medium.bin) |

---

## ⚙️ KEY SETTINGS

Edit `config.json`:
```json
{
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama2",
  "whisper_model": "models/ggml-medium.bin"
}
```

Change model:
```json
{ "ollama_model": "mistral" }        // Faster
{ "ollama_model": "neural-chat" }    // Conversational
{ "ollama_model": "orca" }           // Better quality
```

---

## 🔧 TROUBLESHOOTING

| Issue | Fix |
|-------|-----|
| "Cannot connect to ollama" | Run: `ollama serve` |
| "Module not found" | Run: `pip install -r requirements.txt` |
| "File not found" | Check path spelling & location |
| "Slow processing" | Use faster model or enable GPU |
| "Poor output" | Improve audio quality or refine template |

---

## 📊 PERFORMANCE

| Task | Time |
|------|------|
| 60-min meeting | 15-20 min total |
| Transcription | 5-10 min |
| MOM generation | 1-2 min |
| Batch 10 files | 2-3 hours |

---

## 🚀 3-STEP START

```
1. setup.bat              (one time)
2. ollama serve          (keep running)
3. generate_mom.bat file (run anytime)
```

---

## 📖 DOCUMENTATION MAP

| Document | Purpose | Time |
|----------|---------|------|
| START_HERE.md | This card | 2 min |
| QUICKSTART.md | Fast setup | 5 min |
| README.md | Full guide | 20 min |
| TEMPLATES.md | Customization | 15 min |
| ARCHITECTURE.md | Design | 20 min |
| DEPLOYMENT.md | Production | 20 min |

---

## 💻 EXAMPLES

### Single File
```bash
generate_mom.bat C:\meetings\review.wav
# Output: moms\review_mom.txt
```

### Batch Process
```bash
copy C:\meetings\*.wav recordings\
generate_mom_batch.bat recordings
```

### Custom Format
```bash
python mom_templates.py --add mycorp "Format" "Description" "Prompt"
python mom_generator.py --audio meeting.wav --template mycorp
```

### PowerShell
```powershell
.\manage_mom.ps1 -Action process -AudioFile meeting.wav
```

---

## ✅ CHECKLIST

- [ ] Python 3.7+ installed
- [ ] Ollama installed
- [ ] Run `setup.bat`
- [ ] Ollama running (`ollama serve`)
- [ ] Audio file ready
- [ ] First MOM generated

---

## 🎬 SCRIPTS

| Script | Use For |
|--------|---------|
| `setup.bat` | Initial setup |
| `generate_mom.bat` | Single file |
| `generate_mom_batch.bat` | Directory batch |
| `templates.bat` | Template management |
| `manage_mom.ps1` | Advanced operations |

---

## 🐍 PYTHON MODULES

| Module | Purpose | Lines |
|--------|---------|-------|
| `mom_generator.py` | Main app | 300+ |
| `mom_templates.py` | Templates | 250+ |
| `setup.py` | Setup automation | 200+ |
| `verify_deployment.py` | Verification | 200+ |

---

## 📋 FILE CHECKLIST

**Documentation (8 files)**
- ✅ START_HERE.md
- ✅ QUICKSTART.md
- ✅ README.md
- ✅ TEMPLATES.md
- ✅ ARCHITECTURE.md
- ✅ DEPLOYMENT.md
- ✅ INDEX.md
- ✅ INTEGRATION_SUMMARY.md

**Scripts (5 files)**
- ✅ setup.bat
- ✅ generate_mom.bat
- ✅ generate_mom_batch.bat
- ✅ templates.bat
- ✅ manage_mom.ps1

**Python (4 files)**
- ✅ mom_generator.py
- ✅ mom_templates.py
- ✅ setup.py
- ✅ verify_deployment.py

**Configuration (3 files)**
- ✅ config.json
- ✅ requirements.txt
- ✅ mom_templates.json (auto)

---

## 🎯 NEXT STEPS

### Now
1. Read START_HERE.md (you are here)
2. Run setup.bat

### Today
1. Read QUICKSTART.md
2. Generate first MOM
3. Try different templates

### This Week
1. Read README.md
2. Customize config.json
3. Process all meetings

---

## 🌟 KEY FEATURES

- ✅ Audio transcription (Whisper.cpp)
- ✅ MOM generation (Ollama LLM)
- ✅ 6 built-in templates
- ✅ Batch processing
- ✅ Custom templates
- ✅ Error handling
- ✅ System verification
- ✅ Production ready

---

## 💡 TIPS

**Faster Processing:**
- Use smaller model: `mistral` instead of `llama2`
- Use simpler template: `executive` instead of `technical`
- Process sequentially (default)

**Better Quality:**
- Use larger model: `orca` instead of `llama2`
- Improve audio quality
- Use detailed template
- Enable GPU acceleration

**Custom Templates:**
- Start with built-in template
- Adjust prompt for your needs
- Test with sample file
- Save and reuse

---

## 🆘 HELP

### Command Help
```bash
python mom_generator.py --help
python mom_templates.py --help
python setup.py --help
```

### System Check
```bash
python verify_deployment.py
```

### Full Documentation
→ See README.md

---

## 📞 QUICK CONTACTS

**Ollama Issues:** https://ollama.ai
**Python Issues:** https://python.org
**Windows Issues:** https://microsoft.com

---

## 🎉 READY TO GO!

Your system is complete and ready to use.

**Start:** Run `setup.bat`  
**Learn:** Read `QUICKSTART.md`  
**Use:** Run `generate_mom.bat file.wav`

---

**Version:** 1.0  
**Status:** ✅ Complete  
**Ready:** Yes!

Save this card for quick reference!
