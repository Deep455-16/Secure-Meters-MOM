# 🔐 Security Policy

MOM Generator is designed as a **fully offline, locally operated** tool. Meeting audio, transcripts and generated minutes are processed on the user's own machine and are never sent to external services.

---

## 1. Security Model

| Principle | Implementation |
|---|---|
| **Local-only processing** | Speech-to-text (Whisper) and summarisation (Ollama + Qwen2.5) run on-device |
| **No cloud dependency** | No API keys, accounts, telemetry or third-party AI services |
| **Localhost access** | Web UI and API are served at `http://127.0.0.1:5001` |
| **No data retention by vendor** | There is no vendor server; data exists only on your disk |
| **User-controlled settings** | Stored in a local `config.json`; contains no credentials |

### Trust boundaries

```text
┌──────────────────────── Your PC (trusted boundary) ────────────────────────┐
│  Browser ⇄ mom_api_server.py (127.0.0.1:5001) ⇄ Whisper / Ollama (local)   │
│                         │                                                  │
│                         └──► DOCX / PDF / TXT files saved locally          │
└────────────────────────────────────────────────────────────────────────────┘
        ▲ Internet used ONLY for: initial install, `ollama pull`, model updates
```

---

## 2. Network Activity

| When | Destination | Purpose |
|---|---|---|
| Installation (`setup.bat` / `setup.sh`) | Python, Ollama and package sources | Install dependencies |
| `ollama pull` / `START_APP` model refresh | Ollama model registry | Download or update models |
| Normal operation | **None** | Fully offline |

> 💡 After installation and model download, you can disconnect from the internet entirely. For air-gapped environments, skip the auto-update step and pre-load models manually.

---

## 3. Data Handling

- **Audio / transcripts / MOMs** are written only to local folders on the machine running the app.
- **Sensitive meetings:** delete recordings, transcripts and exports once no longer needed.
- **Backups and sync:** keep the app folder out of cloud-synced directories (OneDrive, Dropbox, iCloud) if confidentiality is required.
- **Logs:** terminal output may include file names or processing messages. Do not share screenshots publicly without reviewing them.

---

## 4. Hardening Checklist

- [ ] Run the app only on a **trusted, single-user** machine.
- [ ] Keep the server bound to **`127.0.0.1`** — do **not** expose port `5001` to your LAN or the internet (no port-forwarding, tunnels or `0.0.0.0` binding).
- [ ] Keep the OS firewall enabled; block inbound connections to port `5001` and Ollama's port (`11434`).
- [ ] Use **full-disk encryption** (BitLocker / FileVault).
- [ ] Use a standard user account for daily use; admin rights only for `setup.bat`.
- [ ] Download the project only from your organisation's trusted source and review `setup.bat` / `setup.sh` before running with elevated privileges.
- [ ] Keep Python, Ollama and dependencies updated.
- [ ] Restrict file permissions on the folder holding recordings and exports.
- [ ] Close the terminal window when finished to stop the server.

---

## 5. Known Limitations

- **No built-in authentication.** Anyone with access to the local machine session can open the app. Rely on OS-level account security and screen locking.
- **Local LLM output is not guaranteed to be accurate.** Always review generated minutes before circulating them, especially for decisions and action items.
- **Uploaded files are processed as-is.** Only upload audio and text from sources you trust.
- **Setup scripts install software** (Python, Ollama) and may require administrator rights.

---

## 6. Supported Versions

Only the latest version on the main branch receives security fixes.

| Version | Supported |
|---|:---:|
| Latest (`main`) | ✅ |
| Older snapshots | ❌ |

---

## 7. Reporting a Vulnerability

Please **do not open a public issue** for security problems.

1. Contact the maintainer / your IT administrator privately at: **`<security-contact@your-organisation.com>`** *(replace with your real address)*.
2. Include:
   - A clear description of the issue and its impact
   - Steps to reproduce
   - Affected OS, Python and Ollama versions
   - Any logs or screenshots (with sensitive content removed)
3. You can expect:
   - Acknowledgement within **3 business days**
   - An initial assessment within **7 days**
   - A fix or mitigation plan communicated once the issue is confirmed

Please allow reasonable time for a fix before any public disclosure.

---

## 8. Scope

**In scope:** `mom_api_server.py`, files under `source code/backend` and `source code/frontend`, install and start scripts, handling of `config.json`.

**Out of scope:** vulnerabilities in third-party components (Python, Ollama, Whisper, Qwen models) — please report those to their respective maintainers — and issues requiring physical or administrator access to the host machine.

---

## 9. Responsible Use

Record and transcribe meetings only with the **consent of all participants** and in line with your organisation's policies and applicable laws.

---

*Last updated: November 2026*
