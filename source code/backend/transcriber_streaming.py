import threading
import queue
import numpy as np
import logging
from faster_whisper import WhisperModel
import warnings

logger = logging.getLogger(__name__)

class StreamingTranscriber:
    """
    Background worker that runs a single whisper model on queued audio segments.
    """
    def __init__(self, device="cpu", model_size="small"):
        logger.info(f"Loading whisper model ({model_size}) on {device}...")
        try:
            warnings.filterwarnings("ignore", category=UserWarning)
            # Use the specified model size (e.g. 'small' for Hinglish, 'distil-small.en' for English)
            self.model = WhisperModel(model_size, device=device, compute_type="int8")
            logger.info(f"Whisper model ({model_size}) loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load whisper model: {e}")
            self.model = None

        self.audio_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        
        # Callback to pass the transcribed text
        self.on_transcription_callback = None

    def start(self):
        if not self.model:
            logger.error("Cannot start ASR: model not loaded.")
            return

        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        
        logger.info("Streaming ASR worker thread started.")

    def stop(self):
        self.is_running = False
        
        # Instantly drop all pending audio chunks
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.task_done()
            except queue.Empty:
                break
                
        if self.worker_thread:
            self.worker_thread.join(timeout=0.5)
            
        logger.info("Streaming ASR stopped, pending audio discarded.")

    def add_audio_segment(self, pcm_bytes: bytes):
        """Add a complete speech segment from VAD to the transcription queue."""
        self.audio_queue.put(pcm_bytes)

    def _process_queue(self):
        while self.is_running:
            try:
                pcm_bytes = self.audio_queue.get(timeout=1.0)
                audio_array = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Transcribe audio as-is — Hinglish (Hindi words in Roman script + English)
                # is preserved naturally in the transcript without any forced translation.
                # The MOM generation layer will synthesize everything into English.
                segments, info = self.model.transcribe(
                    audio_array,
                    beam_size=3,                      # slightly faster than default 5
                    condition_on_previous_text=False,  # prevents hallucination loops
                    vad_filter=True,                   # skip silent segments automatically
                    vad_parameters=dict(min_silence_duration_ms=400)
                )
                text = " ".join([seg.text for seg in segments]).strip()
                
                if text and self.on_transcription_callback:
                    self.on_transcription_callback(text)
                
                self.audio_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in transcription worker: {e}")
