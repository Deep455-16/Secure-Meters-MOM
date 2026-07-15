"""
MOM (Minutes of Meeting) Generator
Integrates whisper.cpp for transcription with ollama for MOM generation
"""

import os

# Fix Windows WinError 1314 by forcing huggingface_hub to disable symlinks BEFORE imports
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

import subprocess
import json
import requests
import math
import time
import tempfile
import concurrent.futures
from pathlib import Path
from typing import Optional, Dict
import logging

try:
    from mom_templates import MOMTemplateManager
    TEMPLATES_AVAILABLE = True
except ImportError:
    TEMPLATES_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """Handles audio transcription using openai-whisper"""
    
    def __init__(self, whisper_exe_path: str, model_path: str):
        from faster_whisper import WhisperModel
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        
        # By default, use the incredibly fast distil-small.en
        model_size = "distil-small.en"
        
        # Override if specific sizes are requested in config
        if "medium" in model_path.lower() and "distil" not in model_path.lower(): 
            model_size = "medium"  # Standard medium for multilingual translation
        elif "small" in model_path.lower(): 
            model_size = "distil-small.en" if "distil" in model_path.lower() else "small"
        elif "large" in model_path.lower() or "turbo" in model_path.lower(): model_size = "large-v3-turbo"
        elif "tiny" in model_path.lower(): model_size = "tiny"
        elif "base" in model_path.lower(): model_size = "base"
        
        logger.info(f"Loading Faster-Whisper model '{model_size}'...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.model_size = model_size
        logger.info("Faster-Whisper model loaded successfully.")
        
    def transcribe(self, audio_file: str, output_file: Optional[str] = None, auto_translate: bool = True, language: Optional[str] = None) -> Dict[str, str]:
        """
        Transcribe audio file using openai-whisper
        
        Args:
            audio_file: Path to audio file
            output_file: Optional output file path for transcript
            auto_translate: Whether to automatically detect language and translate to English
            language: Optional language code to force (bypasses detection phase for speed)
            
        Returns:
            Dictionary containing 'text' and 'language'
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        logger.info(f"Starting transcription of {audio_file}")
        
        try:
            # Note: distilled models don't support translation, so we handle it gracefully
            kwargs = {}
            if auto_translate and "distil" not in self.model_size:
                kwargs["task"] = "translate"
            if language:
                kwargs["language"] = language
                
            segments, info = self.model.transcribe(audio_file, **kwargs)
            
            # Faster-whisper returns a generator, so we must iterate it to perform the transcription
            transcript = " ".join([segment.text for segment in segments]).strip()
            detected_lang = info.language
            
            logger.info(f"Transcription completed (Language: {detected_lang})")
            
            # Save transcript if output file specified
            if output_file:
                os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                logger.info(f"Transcript saved to {output_file}")
            
            return {'text': transcript, 'language': detected_lang}
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise


class OllamaClient:
    """Handles communication with ollama servers"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.base_url = ollama_url.rstrip('/')
        
    def check_and_update_ollama(self):
        """Check GitHub for newer version of Ollama and silently update via winget if found."""
        try:
            import subprocess
            import re
            
            # 1. Get current version
            CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            if result.returncode != 0:
                return
                
            current_ver_str = result.stdout.strip()
            match = re.search(r'version is (\d+\.\d+\.\d+)', current_ver_str)
            if not match:
                return
                
            current_ver = match.group(1)
            
            # 2. Get latest version from GitHub
            resp = requests.get("https://api.github.com/repos/ollama/ollama/releases/latest", timeout=5)
            if resp.status_code != 200:
                return
                
            latest_ver_str = resp.json().get('tag_name', '')
            latest_match = re.search(r'(\d+\.\d+\.\d+)', latest_ver_str)
            if not latest_match:
                return
                
            latest_ver = latest_match.group(1)
            
            # 3. Compare versions
            curr_tuple = tuple(map(int, current_ver.split('.')))
            latest_tuple = tuple(map(int, latest_ver.split('.')))
            
            if latest_tuple > curr_tuple:
                logger.info(f"New Ollama version available: {latest_ver} (Current: {current_ver}). Automatically updating...")
                print(f"\n[!] New Ollama version detected: {latest_ver} (Current: {current_ver})")
                print("📦 Downloading and installing update in the background via winget. This may take a minute...")
                
                update_cmd = ["winget", "upgrade", "--id", "Ollama.Ollama", "--silent", "--accept-package-agreements", "--accept-source-agreements"]
                
                update_result = subprocess.run(update_cmd, creationflags=CREATE_NO_WINDOW, capture_output=True, text=True)
                if update_result.returncode == 0 or 'No newer package versions' not in update_result.stdout:
                    logger.info("Ollama updated successfully.")
                    print("✓ Ollama update installed successfully!\n")
                else:
                    logger.warning(f"Failed to update Ollama automatically via winget.")
                    print("✗ Automatic update encountered an issue, continuing with the current version.\n")
                    
        except Exception as e:
            logger.warning(f"Ollama auto-update check failed safely: {e}")

    def verify_connection(self) -> dict:
        """Verify Ollama server is reachable and return status info. Attempts auto-start if down."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            logger.info(f"Ollama connected. Available models: {model_names}")
            return {'connected': True, 'models': model_names}
        except requests.exceptions.ConnectionError:
            logger.warning(f"Cannot connect to Ollama at {self.base_url}. Attempting to auto-start 'ollama serve'...")
            try:
                # Attempt to launch Ollama silently in the background
                import subprocess
                import time
                CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
                subprocess.Popen(["ollama", "serve"], creationflags=CREATE_NO_WINDOW)
                
                # Wait up to 5 seconds for it to bind
                for _ in range(5):
                    time.sleep(1)
                    try:
                        resp = requests.get(f"{self.base_url}/api/tags")
                        if resp.status_code == 200:
                            models = resp.json().get('models', [])
                            model_names = [m['name'] for m in models]
                            logger.info(f"Ollama auto-started successfully. Available models: {model_names}")
                            return {'connected': True, 'models': model_names}
                    except requests.exceptions.ConnectionError:
                        continue
                        
                return {'connected': False, 'models': [], 'error': 'Ollama server is not running and could not be started automatically. Please open the Ollama app from your Start Menu.'}
            except Exception as auto_start_err:
                logger.error(f"Failed to auto-start Ollama: {auto_start_err}")
                return {'connected': False, 'models': [], 'error': 'Ollama server is not running. Please open the Ollama app from your Start Menu.'}
        except Exception as e:
            logger.error(f"Ollama connection check failed: {str(e)}")
            return {'connected': False, 'models': [], 'error': str(e)}
        
    def list_models(self) -> list:
        """List available models on ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get('models', [])
            return [m['name'] for m in models]
        except requests.exceptions.ConnectionError:
            # Suppress noisy logs if Ollama is restarting or updating in the background
            return []
        except Exception as e:
            logger.debug(f"Failed to list ollama models: {str(e)}")
            return []

    # ── Language Detection & Translation ─────────────────────────────────────

    def _detect_language(self, text: str) -> str:
        """
        Detect transcript language using Unicode character-ratio analysis.
        No external libraries required — works offline.

        Devanagari Unicode block: U+0900–U+097F
        Returns:
            'hindi'    — >40% of alphabetic chars are Devanagari (pure Hindi)
            'hinglish' —  5%–40% Devanagari (mixed Hindi/English script)
            'english'  —  <5%  Devanagari (mostly Latin script)
        """
        if not text:
            return 'english'
        alpha_chars = [c for c in text if c.isalpha()]
        if not alpha_chars:
            return 'english'
        deva_count = sum(1 for c in alpha_chars if '\u0900' <= c <= '\u097F')
        deva_ratio = deva_count / len(alpha_chars)
        if deva_ratio > 0.40:
            detected = 'hindi'
        elif deva_ratio > 0.05:
            detected = 'hinglish'
        else:
            detected = 'english'
        logger.info(
            f"Language detection: {detected} "
            f"(Devanagari ratio: {deva_ratio:.1%}, sample size: {len(alpha_chars)} chars)"
        )
        return detected

    def _translate_chunk(self, text: str, model: str) -> str:
        """
        Translate a single chunk of Hindi text to fluent English using Ollama.
        The model is already warm (preloaded), so this is fast.
        """
        prompt = (
            "Translate the following meeting transcript from Hindi to English.\n"
            "Rules:\n"
            "- Output ONLY the English translation. Do NOT include any commentary.\n"
            "- Keep all names, numbers, technical terms, and product names unchanged.\n"
            "- Preserve the conversational flow and meaning accurately.\n"
            "- If a sentence is already in English, keep it exactly as-is.\n\n"
            f"Hindi Transcript:\n{text}"
        )
        # Token budget: Hindi chars / 3 ≈ word count; * 1.5 for English expansion
        word_estimate = max(len(text) // 3, 150)
        return self._call_generate(model, prompt, word_limit=word_estimate)

    def _translate_hindi_to_english(self, text: str, model: str) -> str:
        """
        Translate a full Hindi (Devanagari) meeting transcript to English.
        Long transcripts are split into chunks to stay within model context.
        The model is already preloaded, so each call is fast.
        """
        MAX_TRANSLATE_CHUNK = 6000  # chars per chunk for translation
        if len(text) <= MAX_TRANSLATE_CHUNK:
            logger.info("Translating Hindi transcript to English...")
            result = self._translate_chunk(text, model)
            logger.info("Translation complete.")
            return result

        # Long transcript: translate chunk by chunk
        parts = self._chunk_transcript(text, chunk_size=MAX_TRANSLATE_CHUNK)
        logger.info(f"Translating Hindi transcript in {len(parts)} parts...")
        translated_parts = []
        for i, part in enumerate(parts, 1):
            logger.info(f"  Translating part {i}/{len(parts)}...")
            translated_parts.append(self._translate_chunk(part, model))
        result = '\n'.join(translated_parts)
        logger.info("Full Hindi translation complete.")
        return result

    # ── Model Utilities ───────────────────────────────────────────────────────

    def _is_qwen3(self, model: str) -> bool:
        """Check if model is a Qwen3 variant (not Qwen2.5)"""
        m = model.lower()
        return "qwen3" in m

    def _get_model_options(self, model: str = "", word_limit: int = 300) -> dict:
        """
        Get optimized inference options.
        - num_predict: generous token budget so MOM is never truncated.
        - temperature: low for deterministic, professional output.
        - think: False for Qwen3 to suppress chain-of-thought (API-level, fastest path).
        """
        # Generous token budget: ~1.8 tokens per word + 256 buffer
        max_tokens = int(word_limit * 1.8) + 256
        max_tokens = max(max_tokens, 1024)  # never less than 1024 tokens

        opts = {
            "num_predict": max_tokens,
            "num_ctx": 8192,          # Cap context to prevent massive VRAM allocation (OOM)
            "temperature": 0.2,       # low = consistent, professional output
            "top_p": 0.85,
            "repeat_penalty": 1.05,
        }
        # Disable chain-of-thought at API level for Qwen3 models
        if self._is_qwen3(model):
            opts["think"] = False
        return opts

    def preload_model(self, model: str):
        """Send a lightweight keep-alive request to preload model into GPU memory"""
        try:
            requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": "", "keep_alive": "10m"}
            )
            logger.info(f"Model '{model}' preloaded into memory.")
        except Exception as e:
            logger.warning(f"Model preload failed (non-critical): {e}")

    def _clean_response(self, text: str) -> str:
        """Strip <think>...</think> blocks and leading/trailing whitespace."""
        import re
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Also strip any residual /no_think markers that old models may echo
        text = re.sub(r'^/no_think\s*', '', text, flags=re.MULTILINE)
        return text.strip()

    def _call_generate(self, model: str, prompt: str, timeout: int = None, word_limit: int = 300) -> str:
        """Call Ollama /api/generate endpoint with optimized options"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "10m",
                "options": self._get_model_options(model, word_limit),
            }
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code != 404:
                error_msg = response.json().get('error', response.text) if response.text else str(e)
                raise RuntimeError(f"Ollama API Error ({response.status_code}): {error_msg}") from e
            raise
        return self._clean_response(response.json().get('response', ''))

    def _call_chat(self, model: str, prompt: str, timeout: int = None, word_limit: int = 300) -> str:
        """Call Ollama /api/chat endpoint (fallback) with optimized options"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "keep_alive": "10m",
                "options": self._get_model_options(model, word_limit),
            }
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_msg = response.json().get('error', response.text) if response.text else str(e)
            raise RuntimeError(f"Ollama API Error ({response.status_code}): {error_msg}") from e
        return self._clean_response(response.json().get('message', {}).get('content', ''))

    def _chunk_transcript(self, transcript: str, chunk_size: int = 10000) -> list:
        """
        Split long transcripts into sentence/paragraph-aware chunks.
        Tries to split at paragraph or sentence boundaries to preserve context.
        """
        if len(transcript) <= chunk_size:
            return [transcript]

        chunks = []
        lines = transcript.split('\n')
        current_chunk: list = []
        current_len = 0

        for line in lines:
            line_len = len(line) + 1  # +1 for newline
            # If adding this line would exceed chunk_size, flush current chunk
            if current_len + line_len > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_len = 0
            current_chunk.append(line)
            current_len += line_len

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        logger.info(f"Transcript split into {len(chunks)} chunks (total {len(transcript)} chars)")
        return chunks

    def _summarize_chunk(self, chunk: str, model: str, chunk_idx: int,
                         total: int, source_lang: str = 'english') -> str:
        """
        Summarize a single transcript chunk into structured bullet points.
        source_lang: 'english', 'hindi' (already translated), or 'hinglish'
        """
        # Extra instruction injected only for Hinglish (Hindi already translated before chunking)
        if source_lang == 'hinglish':
            lang_note = (
                "IMPORTANT: The transcript is in Hinglish (a mix of Hindi and English).\n"
                "You MUST read and understand both languages simultaneously.\n"
                "Your output MUST be in professional English only — translate any Hindi you see.\n"
            )
        else:
            lang_note = "Output in professional English.\n"

        prompt = (
            f"You are summarizing part {chunk_idx} of {total} of a meeting transcript.\n"
            + lang_note +
            "Extract ONLY the following from this portion (bullet points only, be concise):\n"
            "- Topics discussed\n"
            "- Key decisions made\n"
            "- Action items (only if owner names are explicitly spoken)\n"
            "Do NOT fabricate names or details. Do NOT write intro/conclusion sentences.\n\n"
            f"Transcript portion:\n{chunk}"
        )
        return self._call_generate(model, prompt, word_limit=250)

    def _merge_summaries(self, summaries: list, model: str, word_limit: int, current_date: str) -> str:
        """Merge chunk summaries into a final polished MOM. Uses hierarchical merging for huge transcripts."""
        # Step 1: Hierarchical batching if too many summaries (prevents context overflow 500 errors)
        BATCH_SIZE = 12
        while len(summaries) > BATCH_SIZE:
            logger.info(f"Hierarchical merge: condensing {len(summaries)} summaries into batches of {BATCH_SIZE}...")
            next_level = []
            for i in range(0, len(summaries), BATCH_SIZE):
                batch = summaries[i:i+BATCH_SIZE]
                combined_batch = '\n\n---\n\n'.join(f"[Part {j+1}]\n{s}" for j, s in enumerate(batch))
                
                prompt = (
                    "You are condensing multiple meeting summaries into a single cohesive summary.\n"
                    "Extract all major topics, key decisions, and action items. Remove redundancies.\n"
                    "Do NOT write an intro or conclusion. Output clear bullet points.\n\n"
                    f"Summaries to condense:\n{combined_batch}"
                )
                logger.info(f"  Condensing batch {i//BATCH_SIZE + 1}...")
                next_level.append(self._call_generate(model, prompt, word_limit=400))
            summaries = next_level

        # Step 2: Final merge into MOM format
        combined = '\n\n---\n\n'.join(
            f"[Part {i+1}]\n{s}" for i, s in enumerate(summaries)
        )
        prompt = (
            f"You are writing Minutes of Meeting (MOM) dated {current_date}.\n"
            "Below are structured summaries from different parts of the same meeting.\n"
            "Produce a single, clean, professional MOM using EXACTLY this format:\n\n"
            "**MINUTES OF MEETING**\n"
            f"Date: {current_date}\n\n"
            "**1. Agenda / Topics Discussed**\n"
            "**2. Key Discussion Points**\n"
            "**3. Decisions Taken**\n"
            "**4. Action Items**\n"
            "**5. Next Steps**\n\n"
            f"Rules:\n"
            f"- Total length: approximately {word_limit} words.\n"
            "- Merge duplicate points. Remove all redundancy.\n"
            "- Professional English only.\n"
            "- Action items: only include owners if their names appear explicitly in the summaries.\n"
            "- Do NOT add any commentary, preamble, or closing remarks outside the MOM structure.\n\n"
            f"Meeting Summaries:\n{combined}"
        )
        return self._call_generate(model, prompt, word_limit=word_limit)
    
    def generate_mom(self, transcript: str, model: str = "qwen2.5:1.5b",
                     template: str = None, word_limit: int = 300,
                     refinement_model: str = "qwen2.5:7b") -> str:
        """
        Generate a full, structured MOM from the transcript.

        Language handling:
          - Hindi (Devanagari >40%): pre-translated to English, then standard pipeline
          - Hinglish (mixed 5–40%):  single-pass bilingual prompt
          - English (<5% Devanagari): standard pipeline, no change

        Length handling:
          - Short (<= 12000 chars after any translation): single-pass generation
          - Long: chunk-and-merge strategy
        """
        from datetime import datetime
        current_date = datetime.now().strftime('%B %d, %Y')

        # ── Verify Ollama connection ──────────────────────────────────
        status = self.verify_connection()
        if not status['connected']:
            raise RuntimeError(
                f"Ollama server not accessible at {self.base_url}. "
                "Please ensure 'ollama serve' is running."
            )

        # ── Model resolution ─────────────────────────────────────────
        available_models = status.get('models', [])
        
        # Resolve chunking model
        if model not in available_models:
            matched = next((m for m in available_models if m.startswith(model.split(':')[0])), None)
            if matched:
                logger.info(f"Chunking model '{model}' not found, using closest match: '{matched}'")
                model = matched
            elif available_models:
                model = available_models[0]
                logger.warning(f"Requested chunking model not found. Falling back to: '{model}'")
            else:
                raise RuntimeError("No models available in Ollama. Run: ollama pull qwen2.5:1.5b")
                
        # Resolve refinement model
        if refinement_model not in available_models:
            matched = next((m for m in available_models if m.startswith(refinement_model.split(':')[0])), None)
            if matched:
                logger.info(f"Refinement model '{refinement_model}' not found, using closest match: '{matched}'")
                refinement_model = matched
            else:
                refinement_model = model
                logger.warning(f"Requested refinement model not found. Falling back to chunking model: '{model}'")

        # ── Preload model to minimise first-token latency ─────────────
        self.preload_model(model)
        if model != refinement_model:
            self.preload_model(refinement_model)

        # ── Language detection & pre-translation ─────────────────────
        source_lang = self._detect_language(transcript)

        if source_lang == 'hindi':
            # Pre-translate Devanagari Hindi → English.
            # Model is already warm → this is fast.
            # After translation the standard English pipeline runs at full speed.
            logger.info("Hindi transcript detected — pre-translating to English.")
            transcript = self._translate_hindi_to_english(transcript, model)
            source_lang = 'english'   # now fully English
        elif source_lang == 'hinglish':
            logger.info(
                "Hinglish/mixed transcript detected — "
                "using bilingual single-pass generation."
            )
            # No pre-translation; the model reads mixed input and outputs English MOM.
        else:
            logger.info("English transcript detected — standard pipeline.")

        # ── Chunk-and-merge for long transcripts ─────────────────────
        CHUNK_THRESHOLD = 12000
        if len(transcript) > CHUNK_THRESHOLD:
            logger.info(
                f"Long transcript ({len(transcript)} chars) — using chunk-and-merge strategy"
            )
            chunks = self._chunk_transcript(transcript, chunk_size=10000)
            summaries = []
            for i, chunk in enumerate(chunks, 1):
                logger.info(f"Summarizing chunk {i}/{len(chunks)}...")
                summary = self._summarize_chunk(
                    chunk, model, i, len(chunks), source_lang=source_lang
                )
                summaries.append(summary)
            mom = self._merge_summaries(summaries, refinement_model, word_limit, current_date)
            logger.info("MOM generation completed via chunk-and-merge")
            return mom

        # ── Single-pass for short/medium transcripts ─────────────────
        prompt = self._build_prompt(
            transcript, refinement_model, template, current_date, word_limit,
            source_lang=source_lang
        )

        try:
            logger.info(f"Generating MOM using model: {refinement_model}")
            try:
                mom = self._call_generate(refinement_model, prompt, word_limit=word_limit)
                logger.info("MOM generation completed via /api/generate")
                return mom
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    logger.warning("/api/generate returned 404, retrying via /api/chat...")
                else:
                    raise

            mom = self._call_chat(refinement_model, prompt, word_limit=word_limit)
            logger.info("MOM generation completed via /api/chat")
            return mom

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Ollama server not accessible at {self.base_url}. Run: ollama serve"
            )
        except Exception as e:
            logger.error(f"MOM generation failed: {str(e)}")
            raise

    def _build_prompt(self, transcript: str, model: str, template: str,
                      current_date: str, word_limit: int,
                      source_lang: str = 'english') -> str:
        """
        Build the MOM generation prompt.
        source_lang: 'english', 'hindi' (already pre-translated), or 'hinglish'
        Uses a template if provided and available, otherwise the robust default.
        """
        # Craft the language instruction block based on source
        if source_lang == 'hinglish':
            lang_rule = (
                "LANGUAGE RULE (CRITICAL): The transcript is in Hinglish — a mix of "
                "Hindi and English spoken together. You MUST read and fully understand "
                "BOTH languages simultaneously to extract the complete meaning. "
                "Your entire MOM output MUST be in professional English only. "
                "Translate any Hindi phrases you encounter as you write."
            )
        else:
            # English (or pre-translated Hindi — both treated the same here)
            lang_rule = (
                "LANGUAGE RULE: Output MUST be in professional English only. "
                "If any non-English text remains, translate it."
            )

        # ── Template-based prompt ─────────────────────────────────────
        if template and TEMPLATES_AVAILABLE and template not in ('dynamic', None):
            template_obj = MOMTemplateManager.get_template(template)
            if template_obj:
                base = template_obj['prompt'].format(
                    transcript=transcript, date=current_date
                )
                return (
                    base
                    + f"\n\nSTRICT RULES:\n"
                    + f"1. Total MOM length: approximately {word_limit} words.\n"
                    + f"2. {lang_rule}\n"
                    + "3. Structure: Date → Agenda → Key Discussion Points → Decisions → Action Items → Next Steps.\n"
                    + "4. Participants: ONLY list names EXPLICITLY spoken in the transcript. "
                    + "NEVER fabricate names. Omit this section if no names appear.\n"
                    + "5. Focus on TOPICS and DECISIONS — do NOT repeat dialogue verbatim."
                )
            else:
                logger.warning(f"Template '{template}' not found — using default prompt.")

        # ── Default robust prompt ─────────────────────────────────────
        return (
            "You are a professional meeting secretary.\n"
            f"{lang_rule}\n\n"
            "Write a complete Minutes of Meeting (MOM) from the transcript below.\n"
            "Focus on the TOPICS DISCUSSED, key decisions, and action items — "
            "not on who said what verbatim.\n\n"
            "Use EXACTLY this structure (no extra sections, no preamble):\n\n"
            "**MINUTES OF MEETING**\n"
            f"Date: {current_date}\n\n"
            "**1. Agenda / Topics Discussed**\n"
            "   - [Each major topic as a clear bullet]\n\n"
            "**2. Key Discussion Points**\n"
            "   - [Concise bullets summarising what was discussed per topic. "
            "Capture the substance, not the conversation.]\n\n"
            "**3. Decisions Taken**\n"
            "   - [Each decision stated clearly and completely]\n\n"
            "**4. Action Items**\n"
            "   - [Task] — Owner: [Name if explicitly spoken, else TBD] "
            "— Deadline: [if mentioned, else TBD]\n\n"
            "**5. Next Steps**\n"
            "   - [What happens next / follow-ups planned]\n\n"
            "STRICT RULES:\n"
            f"1. Target length: approximately {word_limit} words.\n"
            "2. Extract and summarise meaning — do NOT copy dialogue verbatim.\n"
            "3. Action Item owners: ONLY use names EXPLICITLY spoken. NEVER invent names.\n"
            "4. If a section has no content, write 'None' — do NOT omit the section.\n"
            "5. Do NOT add closing remarks or 'Here is the MOM' style preamble.\n\n"
            f"Meeting Transcript:\n{transcript}"
        )


class MOMGenerator:
    """Main orchestrator for the MOM generation pipeline"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.transcriber = WhisperTranscriber(
            self.config['whisper_exe'],
            self.config['whisper_model']
        )
        self.ollama = OllamaClient(self.config['ollama_url'])
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _get_ffmpeg_path(self) -> str:
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            return "ffmpeg"
            
    def _get_audio_duration(self, audio_file: str) -> float:
        try:
            ffmpeg_path = self._get_ffmpeg_path()
            cmd = [ffmpeg_path, "-i", audio_file]
            CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            
            import re
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", result.stderr)
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                seconds = float(match.group(3))
                return (hours * 3600) + (minutes * 60) + seconds
            return 0.0
        except Exception as e:
            logger.error(f"Error getting duration: {e}")
            return 0.0

    def _split_audio(self, audio_file: str, output_dir: str, chunk_minutes: int = 5, overlap_seconds: int = 3) -> list:
        duration = self._get_audio_duration(audio_file)
        if duration <= 0:
            logger.warning("Could not determine duration, assuming short file and returning whole file.")
            return [audio_file]
            
        chunk_seconds = chunk_minutes * 60
        if duration <= chunk_seconds:
            return [audio_file]
            
        logger.info(f"Splitting {duration}s audio into ~{chunk_minutes}m chunks with {overlap_seconds}s overlap...")
        chunks = []
        start_time = 0.0
        idx = 0
        
        while start_time < duration:
            chunk_path = os.path.join(output_dir, f"chunk_{idx:03d}.wav")
            # We enforce standard 16kHz Mono PCM WAV to guarantee Whisper works flawlessly
            ffmpeg_path = self._get_ffmpeg_path()
            cmd = [
                ffmpeg_path, "-y", "-i", audio_file,
                "-ss", str(start_time), "-t", str(chunk_seconds + overlap_seconds),
                "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
                "-loglevel", "error", chunk_path
            ]
            CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            subprocess.run(cmd, check=True, creationflags=CREATE_NO_WINDOW)
            chunks.append(chunk_path)
            
            start_time += chunk_seconds
            idx += 1
            
        return chunks
        
    def _process_single_chunk(self, chunk_path: str, chunk_idx: int, total_chunks: int, language: Optional[str] = None) -> str:
        logger.info(f"Processing chunk {chunk_idx + 1}/{total_chunks}...")
        try:
            # Transcribe with Whisper (skipping refinement phase for speed)
            result = self.transcriber.transcribe(chunk_path, auto_translate=True, language=language)
            raw_text = result.get('text', '') if isinstance(result, dict) else result
            
            if not raw_text or not raw_text.strip():
                return ""
                
            return raw_text.strip()
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_idx + 1}: {e}")
            return ""

    def process_meeting(self, audio_file: str, output_dir: Optional[str] = None, template: str = None, word_limit: int = 300, progress_callback=None) -> Dict:
        """
        Process a meeting recording from audio to MOM (with parallel chunking & refinement)
        """
        if output_dir is None:
            output_dir = self.config.get('output_dir', 'MOM_Outputs')
            
        base_name = Path(audio_file).stem
        transcript_file = os.path.join(output_dir, 'transcripts', f"{base_name}.txt")
        mom_file = os.path.join(output_dir, 'moms', f"{base_name}_mom.txt")
        
        os.makedirs(os.path.dirname(transcript_file), exist_ok=True)
        os.makedirs(os.path.dirname(mom_file), exist_ok=True)
        
        # Create a temp directory for chunks
        temp_dir = tempfile.mkdtemp(prefix="mom_chunks_")
        
        # Override transcriber specifically for file upload to guarantee speed with multilingual support
        if self.transcriber.model_size != 'tiny':
            logger.info("Switching to 'tiny' multilingual model for blazing fast file transcription...")
            self.transcriber = WhisperTranscriber('', 'tiny')
            
        if progress_callback: progress_callback(5, "Splitting audio into chunks...")
        
        try:
            chunks = self._split_audio(audio_file, temp_dir, chunk_minutes=5, overlap_seconds=3)
            
            if len(chunks) == 1:
                if progress_callback: progress_callback(40, "Transcribing standard audio file...")
                # Fallback to standard sequential processing for short files
                transcript_text = self.transcriber.transcribe(audio_file).get('text', '')
            else:
                if progress_callback: progress_callback(10, "Detecting language from first chunk...")
                # Detect common language from the first chunk to speed up parallel workers
                logger.info("Detecting primary language from the first chunk to speed up remaining chunks...")
                first_chunk_result = self.transcriber.transcribe(chunks[0], auto_translate=True)
                common_language = first_chunk_result.get('language') if isinstance(first_chunk_result, dict) else None
                
                # Parallel processing for remaining chunks
                logger.info(f"Initiating fast parallel transcription for {len(chunks)} chunks (Language forced to: {common_language})...")
                chunk_results = [""] * len(chunks)
                chunk_results[0] = first_chunk_result.get('text', '') if isinstance(first_chunk_result, dict) else first_chunk_result
                
                max_workers = min(4, len(chunks) - 1)
                if max_workers > 0:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = {
                            executor.submit(self._process_single_chunk, chunk, idx, len(chunks), common_language): idx
                            for idx, chunk in enumerate(chunks[1:], start=1)
                        }
                        
                        completed = 1
                        for future in concurrent.futures.as_completed(futures):
                            idx = futures[future]
                            chunk_results[idx] = future.result()
                            completed += 1
                            if progress_callback:
                                pct = 10 + int((completed / len(chunks)) * 75)
                                progress_callback(pct, f"Transcribing parallel chunks ({completed}/{len(chunks)})...")
                        
                # Merge chunk transcripts smoothly
                logger.info("Merging processed chunks...")
                transcript_text = "\n\n".join([t for t in chunk_results if t and t.strip()])
                
            # Save final refined transcript
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
                
            # Final MOM Generation
            mom_model = self.config.get('ollama_model', 'qwen2.5:7b')
            logger.info(f"Generating final MOM using {mom_model}...")
            if progress_callback: progress_callback(85, f"Generating MOM with {mom_model} (this takes a few minutes)...")
            
            mom = self.ollama.generate_mom(transcript_text, mom_model, template, word_limit)
            
            # Save MOM
            with open(mom_file, 'w', encoding='utf-8') as f:
                f.write(mom)
            logger.info(f"MOM saved to {mom_file}")
            
            if progress_callback: progress_callback(100, "MOM Generation Complete!")
            
            return {
                'audio_file': audio_file,
                'transcript_file': transcript_file,
                'mom_file': mom_file,
                'transcript': transcript_text,
                'mom': mom
            }
        finally:
            # Cleanup temp chunks
            import shutil
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
    
    def batch_process(self, audio_dir: str, output_dir: Optional[str] = None) -> list:
        """
        Process all audio files in a directory
        
        Args:
            audio_dir: Directory containing audio files
            output_dir: Directory to save outputs
            
        Returns:
            List of processing results
        """
        results = []
        audio_extensions = ('.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac', '.mp4')
        
        audio_files = [
            f for f in os.listdir(audio_dir)
            if f.lower().endswith(audio_extensions)
        ]
        
        logger.info(f"Found {len(audio_files)} audio files to process")
        
        for i, audio_file in enumerate(audio_files, 1):
            try:
                audio_path = os.path.join(audio_dir, audio_file)
                logger.info(f"Processing {i}/{len(audio_files)}: {audio_file}")
                result = self.process_meeting(audio_path, output_dir)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {audio_file}: {str(e)}")
                results.append({'audio_file': audio_file, 'error': str(e)})
        
        return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate MOM from meeting recordings')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--audio', required=True, help='Audio file or directory')
    parser.add_argument('--output', help='Output directory (overrides config)')
    parser.add_argument('--template', default='standard', help='MOM template to use (default: standard)')
    parser.add_argument('--batch', action='store_true', help='Process directory of files')
    parser.add_argument('--list-templates', action='store_true', help='List available templates')
    
    args = parser.parse_args()
    
    # List templates if requested
    if args.list_templates:
        if TEMPLATES_AVAILABLE:
            MOMTemplateManager.list_templates()
        else:
            logger.info("Templates module not available")
        return
    
    try:
        generator = MOMGenerator(args.config)
        
        if args.batch or os.path.isdir(args.audio):
            results = generator.batch_process(args.audio, args.output)
            logger.info(f"Batch processing complete. Processed {len(results)} files")
            for result in results:
                if 'error' in result:
                    logger.warning(f"{result['audio_file']}: {result['error']}")
        else:
            result = generator.process_meeting(args.audio, args.output, args.template)
            logger.info(f"Processing complete: {result['mom_file']}")
            print(result['mom'])
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()
