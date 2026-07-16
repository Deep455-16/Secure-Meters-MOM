# 🎙️ MOM Generator — AI Minutes of Meeting

> **Works 100% offline. No cloud. No subscriptions. Your data never leaves your PC.**

Welcome to the Secure Meters MOM Generator! This application uses local AI models to completely automate your meeting minutes, transcribing audio in real-time or from uploads, and generating beautifully formatted DOCX, PDF, and TXT files.

---

## 🚀 Quick Start Guide

### Step 1: One-Time Installation
You only need to do this the very first time you download the application.

**For Windows:**
```text
📁 MOM-main
  └── 📁 install
        └── 📁 Installation-Windows
              └── ▶️  setup.bat   ← Double-click this ONCE
```
A black terminal window will open. **Wait for it to finish.** It will automatically install Python, the Ollama AI engine, and download the necessary AI models (approx. 6 GB). The offline based Ollama AI model Download can sometimes take more time for less configuration PC in such case manually install the models by the following commands:-

Let the installation continue on the specific terminal ,write the following commands on another terminal window after successfull ollama installation only.

1. ollama --version  (For checking the current version of downloaded Ollama model)
2. ollama pull qwen2.5:1.5b  (for downloading the Chunking Model)
3. ollama pull qwen2.5:7b  (for downloading the Refinement Model)
4. ollama list  (After successfull download of the Ollama Models check whether they are downloaded successfully or not)
5. ollama serve  (to check whether the server is started or not once you click on START_APP file after successfull installation)

*Note: This can take 15–25 minutes depending on your internet speed. Grab a coffee!*

**For macOS:**
```text
📁 MOM-main
  └── 📁 install
        └── 📁 Installation-MacOS
              └── 🍎 setup.sh      ← Run this in Terminal ONCE
```
Wait for the installation to complete in your terminal.

### Step 2: Running the Application (Daily Use)
Every time you want to use the MOM Generator:

**For Windows:**
```text
📁 MOM-main
  └── 📁 START_APP
        └── ▶️  START_APP.bat   ← Double-click this every time
```
*Note: This script will also automatically update your AI models in the background if a newer version is available!*

**For macOS:**
```text
📁 MOM-main
  └── 📁 START_APP
        └── 🍎 START_APP.sh    ← Run this in Terminal every time
```

### Step 3: Accessing the App
Once the server starts, your default web browser will automatically open to:
👉 **http://127.0.0.1:5001**

Keep the black terminal window open while you are using the app. When you are finished, simply close the black terminal window to shut down the server.

---

## ⚙️ Configuration & Settings

You can customize almost everything about how the MOM Generator works directly from the app interface without touching any code!

1. Open the app in your browser (http://127.0.0.1:5001).
2. Click the **⚙️ Settings** icon in the top right corner.
3. Any changes you make here are **auto-saved** instantly!

**What you can configure:**
- **AI Models:** Switch between different local models (like `qwen2.5:1.5b` for fast processing or `qwen2.5:7b` for higher quality).
- **Limits:** Adjust the maximum audio upload length (up to 180 mins) and text transcript limits (up to 1,000,000 characters).
- **Word Limits:** Set the target word limit for your generated MOMs (Default: 500 words).
- **Theme:** Toggle between Light and Dark mode using the sun/moon icon at the top right, or set it to Auto to match your system.

---

## 📁 Folder Structure

Here is a quick overview of where everything is located:

```text
📁 MOM-main/
│
├── 📁 START_APP/
│     ├── ▶️  START_APP.bat          ← Launch app on Windows (use daily)
│     └── 🍎 START_APP.sh           ← Launch app on macOS (use daily)
│
├── 🐍  mom_api_server.py           ← Main backend Python server
├── ⚙️  config.json                 ← Saved application settings
├── 📄  README.md                   ← This guide
│
├── 📁 install/
│     ├── 📁 Installation-Windows/  ← Windows setup scripts
│     └── 📁 Installation-MacOS/    ← macOS setup scripts
│
└── 📁 source code/                 ← Application Source Files
      │
      ├── 📁 assets/                ← Images (e.g. SECURE Logo for DOCX templates)
      │
      ├── 📁 backend/               ← AI & Processing Logic
      │     ├── mom_generator.py          (MOM generation engine)
      │     ├── streaming_mom.py          (Live stream pipeline)
      │     ├── transcriber_streaming.py  (Whisper STT engine)
      │     ├── SECURE_MOM_Template.docx  (Base format for exports)
      │     └── ...
      │
      └── 📁 frontend/              ← Web User Interface (HTML/CSS/JS)
            ├── index.html                (Home page)
            ├── live_stream.html          (Live Audio page)
            ├── upload_recording.html     (Audio Upload page)
            ├── text_transcript.html      (Text Input page)
            └── mom_settings.html         (Settings page)
```

---

## 🛠️ Troubleshooting & Common Errors

If something goes wrong, look here first!

### 1. `setup.bat` fails immediately
* **Fix:** Right-click on `setup.bat` and select **"Run as Administrator"**.

### 2. "Python not found" or "Ollama not found" error
* **Fix:** You might need to restart your PC after running the installer for the first time so Windows registers the new software. After restarting, run `setup.bat` again.

### 3. Terminal shows a red "ConnectionError" or "Connection Refused"
* **Fix:** This usually means the Ollama AI engine is restarting or installing an automatic update in the background. Simply wait a minute or two and the app will automatically reconnect. You don't need to do anything!

### 4. Browser says "Site not reachable"
* **Fix:** The server takes a few seconds to load the AI models into memory. Wait 15-30 seconds after double-clicking `START_APP.bat` and then refresh your browser page.

### 5. App opens but MOM generation gets stuck or fails
* **Fix:** Close the terminal window and re-run `START_APP.bat`. If the issue persists, ensure you have enough free RAM (at least 8GB available is recommended) as AI models require significant memory.

---

## 👨‍💻 Manual Server Startup (Advanced)

If you prefer to bypass the automatic startup scripts or are troubleshooting issues, you can launch the server manually:

1. Open a terminal or command prompt in the main `MOM-main` folder.
2. Run the Python backend server:
   ```bash
   python mom_api_server.py
   ```
3. Open your browser and go to `http://127.0.0.1:5001`.

*Make sure Ollama is already running in the background (`ollama serve`) if you choose this manual method.*

---

*For advanced support, please take a screenshot of the black terminal window and share it with your IT administrator or the person who provided you with this application.*
