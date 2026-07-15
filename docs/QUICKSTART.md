# QUICKSTART - MOM Generator

Get Minutes of Meeting (MOM) from audio recordings in 3 steps!

## Step 1: Prerequisites

**Install Ollama:**
- Download from https://ollama.ai
- Run `ollama serve` to start the server
- Run `ollama pull llama2` to get a model

**Check Python:**
- Python 3.7+ should be installed
- Run `python --version` to verify

## Step 2: Setup (One Time)

```batch
setup.bat
```

This will:
- ✓ Check Python installation
- ✓ Verify Whisper.cpp setup
- ✓ Install dependencies
- ✓ Test Ollama connection
- ✓ Create directories

## Step 3: Generate MOM

### Single Audio File
```batch
generate_mom.bat recordings/meeting.wav
```

### All Files in Directory
```batch
generate_mom_batch.bat recordings
```

## Output

Your generated Minutes of Meeting will be in:
```
moms/
  ├── meeting_mom.txt
  └── another_meeting_mom.txt
```

## Audio Files Supported

Place any of these formats in the `recordings/` folder:
- `.wav` - WAV audio
- `.mp3` - MP3 audio  
- `.m4a` - MPEG-4 Audio
- `.flac` - FLAC audio
- `.ogg` - Ogg audio

## What You Get

Generated MOM includes:
1. **Key Discussion Points** - Main topics discussed
2. **Action Items** - Tasks with owners and deadlines
3. **Decisions Made** - Important conclusions
4. **Next Steps** - Follow-up activities
5. **Attendees Summary** - Participants

## Troubleshooting

### "Cannot connect to ollama"
- Ensure ollama is running: `ollama serve`
- Make sure you're on http://localhost:11434

### "Whisper not found"
- Check main.exe exists in current directory
- Check models/ggml-medium.bin exists

### "No models on ollama"
- Run: `ollama pull llama2`
- Or: `ollama pull neural-chat` for other models

## Next Steps

For advanced options, see [README.md](README.md)

- Use custom output directories
- Change Ollama models
- Customize MOM format
- Batch processing

## Example Workflow

```batch
REM 1. First time setup
setup.bat

REM 2. Start ollama server (in another terminal)
ollama serve

REM 3. Place meetings in recordings folder
copy my_meeting.wav recordings/

REM 4. Generate MOM
generate_mom.bat recordings/my_meeting.wav

REM 5. Read MOM
type moms/my_meeting_mom.txt
```

## PowerShell Users

```powershell
# Test environment
.\manage_mom.ps1 -Action test-env

# Process file
.\manage_mom.ps1 -Action process -AudioFile meeting.wav

# Batch process
.\manage_mom.ps1 -Action batch -AudioFile recordings
```

---

**That's it!** You now have an automated system to generate meeting minutes from audio recordings.

For questions or issues, see README.md for detailed documentation.
