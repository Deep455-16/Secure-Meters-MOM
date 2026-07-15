# Integration Architecture Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MOM Generator System                        │
└─────────────────────────────────────────────────────────────────┘

INPUT LAYER
┌─────────────────────┐
│  Audio Recording    │  (MP3, WAV, M4A, FLAC, OGG)
│  (recordings/)      │
└──────────┬──────────┘
           │
           ▼
TRANSCRIPTION LAYER
┌─────────────────────────────────────────┐
│  Whisper.cpp (main.exe)                 │  ASR - Speech to Text
│  Model: ggml-medium.bin                 │
│  Outputs: Transcript                    │
└──────────┬──────────────────────────────┘
           │
           ▼
TRANSCRIPT STORAGE
┌─────────────────────┐
│  Transcripts        │  (transcripts/)
│  .txt files         │
└──────────┬──────────┘
           │
           ▼
GENERATION LAYER
┌─────────────────────────────────────────┐
│  Ollama LLM Server                      │  LLM - Text Generation
│  Models: llama2, neural-chat, etc.      │
│  Templates: standard, executive, tech   │
└──────────┬──────────────────────────────┘
           │
           ▼
OUTPUT LAYER
┌─────────────────────┐
│  Minutes of Meeting │  (moms/)
│  .txt files         │
└─────────────────────┘
```

## Component Details

### 1. Audio Input
- **Supported Formats**: MP3, WAV, M4A, FLAC, OGG
- **Storage**: `recordings/` directory
- **Processing**: Individual files or batch
- **Requirements**: 
  - 8-bit or 16-bit audio
  - Mono or stereo
  - Any sample rate (auto-detected)

### 2. Whisper.cpp (Transcription)
- **Role**: Convert audio to text
- **Binary**: `main.exe`
- **Model**: `models/ggml-medium.bin`
- **Language**: Auto-detected from audio
- **Features**:
  - Multilingual support
  - Timestamp tracking (optional)
  - Speaker diarization (basic)
- **Configuration**: `config.json`

### 3. Transcript Storage
- **Format**: Plain text (.txt)
- **Storage**: `transcripts/` directory
- **Naming**: `{audio_filename}.txt`
- **Content**: Full verbatim transcription
- **Retention**: Permanent (for reference)

### 4. Ollama LLM Server
- **Role**: Generate MOM from transcript
- **URL**: `http://localhost:11434` (default)
- **Available Models**:
  - `llama2` - General purpose (good quality)
  - `neural-chat` - Optimized for conversation
  - `mistral` - Fast, efficient
  - `dolphin` - Creative writing
  - (Many others available)
- **Configuration**: `config.json`
- **Requirements**: 
  - Running ollama server
  - At least one model downloaded

### 5. Template System
- **Role**: Customize MOM format and content
- **Storage**: `mom_templates.json`
- **Built-in Templates**:
  - standard (default)
  - executive (brief)
  - technical (detailed)
  - agile (standup format)
  - client (professional)
  - legal (formal)
- **Customization**: Add/update/delete templates

### 6. MOM Output
- **Format**: Plain text (.txt)
- **Storage**: `moms/` directory
- **Naming**: `{audio_filename}_mom.txt`
- **Content**: Structured minutes including:
  - Discussion points
  - Action items
  - Decisions
  - Next steps
  - Attendees

## Data Flow

### Single File Processing
```
1. User Input
   └─ Audio file path + optional parameters

2. Configuration Load
   └─ Load config.json, config validation

3. Audio Processing
   └─ Execute whisper.cpp
   └─ Create transcript

4. Template Selection
   └─ Load MOM template

5. LLM Processing
   └─ Send transcript + prompt to ollama
   └─ Generate MOM

6. Output Saving
   └─ Save transcript to transcripts/
   └─ Save MOM to moms/

7. Result Return
   └─ Return file paths and content
```

### Batch Processing
```
1. Input Validation
   └─ Verify directory exists

2. File Discovery
   └─ Find all audio files
   └─ Filter by supported extensions

3. Process Each File
   └─ For each audio file:
      ├─ Run single-file pipeline
      ├─ Handle errors gracefully
      └─ Log progress

4. Results Aggregation
   └─ Collect results from all files
   └─ Report successes and failures

5. Summary Output
   └─ Total files processed
   └─ Success/failure counts
```

## Process Specifications

### Whisper.cpp Processing
```
Input:  Audio file (any supported format)
Process: 
  - Detect language
  - Apply noise reduction (optional)
  - Run ASR model inference
  - Generate timestamps
Output: Transcript text
Time:   ~5-30 minutes (depending on duration and quality)
```

### Ollama Processing
```
Input:  Transcript + template prompt
Process:
  - Format prompt with transcript
  - Send to Ollama API
  - LLM generates MOM
  - Format output
Output: Structured MOM text
Time:   ~30 seconds - 5 minutes (model dependent)
```

## Integration Points

### External Services
1. **Ollama Server**
   - REST API at configured URL
   - Requires: `/api/tags` endpoint (list models)
   - Requires: `/api/generate` endpoint (generate text)
   - Connection: HTTP (local by default)

### File System
- **Input**: Audio files in `recordings/`
- **Output**: 
  - Transcripts in `transcripts/`
  - MOMs in `moms/`
- **Config**: `config.json`
- **Templates**: `mom_templates.json`
- **Logs**: Console output (can redirect to file)

### Python Environment
- **Requirements**: Python 3.7+
- **Dependencies**: requests library
- **Scripts**:
  - `mom_generator.py` - Main orchestrator
  - `mom_templates.py` - Template manager
  - `setup.py` - Environment setup

## Error Handling

### Transcription Errors
- **Audio file not found**: Check file path, verify encoding
- **Whisper timeout**: File too large, increase timeout or split
- **Model not found**: Verify model path in config

### LLM Errors
- **Connection refused**: Start ollama server
- **Model not available**: Download model: `ollama pull [modelname]`
- **Timeout**: Model processing taking too long
- **Invalid response**: Ollama server error, check logs

### System Errors
- **Config not found**: Check config.json in working directory
- **Invalid JSON**: Validate config.json syntax
- **Directory not writable**: Check file permissions

## Configuration

### config.json
```json
{
  "whisper_exe": "main.exe",
  "whisper_model": "models/ggml-medium.bin",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama2",
  "output_dir": "."
}
```

### Customization Options
- Change Ollama model for different processing quality
- Adjust Ollama URL for remote servers
- Modify output directories
- Use different Whisper models (base, small, medium, large)

## Performance Characteristics

### Transcription Speed
- **Audio Duration**: 60 minutes
- **Processing Time**: ~10-15 minutes (CPU) / ~2-5 minutes (GPU)
- **File Size**: ~5-20 MB (depends on quality)

### MOM Generation Speed
- **Model**: llama2
- **Processing Time**: ~1-2 minutes per meeting
- **Quality**: High-quality detailed MOM
- **Alternatives**: 
  - mistral (~30 sec, good quality)
  - neural-chat (~1 min, conversational)

### Total Time
- **Single 60-min meeting**: ~15-20 minutes
- **Batch 10 meetings**: ~2-3 hours
- **Bottleneck**: Usually Whisper transcription

## Scaling Considerations

### Single Machine
- **Typical**: 1 audio file at a time
- **Sequential processing**: One after another
- **Resources**: 4-8GB RAM, GPU optional

### Advanced Setup
- **Parallel processing**: Multiple whisper instances
- **Distributed ollama**: Multiple GPU servers
- **Load balancing**: Queue-based processing
- **Caching**: Store transcripts to skip re-processing

## Integration with Other Systems

### Email Integration
```python
# Send MOM via email after generation
import smtplib
with open(mom_file, 'r') as f:
    send_email(recipients, f.read())
```

### Storage Integration
```python
# Upload to cloud storage after generation
import boto3
s3.upload_file(mom_file, bucket, key)
```

### CMS Integration
```python
# Post MOM to content management system
import requests
requests.post(cms_api, data={'content': mom_text})
```

### Slack/Teams Integration
```python
# Send MOM to messaging platform
webhook_url = "..."
requests.post(webhook_url, json={'text': mom_text})
```

## Security Considerations

- **Audio Data**: Stored locally in `recordings/`
- **Transcripts**: Stored locally in `transcripts/`
- **Ollama Access**: Default is localhost only
- **API Keys**: None needed (local setup)
- **Privacy**: All data stays on local machine

For remote Ollama servers:
- Use authentication/API keys
- Implement SSL/TLS encryption
- Control network access

## Monitoring

### Logging
- Console output: Real-time processing updates
- Error tracking: Failed files logged
- Timing: Each step's duration shown

### Health Checks
```bash
# Test environment
python setup.py --quick

# Or with PowerShell
.\manage_mom.ps1 -Action test-env
```

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| Transcription slow | CPU bottleneck | Use GPU or process sequentially |
| Poor transcript quality | Audio quality | Improve audio, use better model |
| MOM too short | Prompt unclear | Refine template prompt |
| Connection refused | Ollama not running | Start ollama: `ollama serve` |
| Out of memory | Large files | Reduce audio quality or split files |

---

For detailed setup, see: [QUICKSTART.md](QUICKSTART.md)
For template customization, see: [TEMPLATES.md](TEMPLATES.md)
For full documentation, see: [README.md](README.md)
