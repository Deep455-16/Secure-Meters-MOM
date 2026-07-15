import collections
import numpy as np
import torch
from silero_vad import load_silero_vad, VADIterator

class VADAudioStream:
    """
    Filters raw audio stream using Silero VAD.
    Expects 16kHz, 16-bit, mono PCM audio bytes.
    """
    def __init__(self, sample_rate=16000, frame_duration_ms=30):
        self.sample_rate = sample_rate
        # Silero VAD expects 512 samples per chunk for 16kHz
        self.frame_size_samples = 512
        self.frame_size_bytes = self.frame_size_samples * 2 # 2 bytes per int16
        
        self.model = load_silero_vad(onnx=True)
        self.vad_iterator = VADIterator(self.model)
        
        self.audio_buffer = bytearray()
        self.current_speech_segment = bytearray()
        self.is_speaking = False

    def process_chunk(self, audio_chunk: bytes) -> list:
        """
        Process incoming raw PCM bytes. 
        Returns a list of completed speech segments (bytes) if any silence gaps were detected.
        """
        self.audio_buffer.extend(audio_chunk)
        completed_segments = []

        while len(self.audio_buffer) >= self.frame_size_bytes:
            frame_bytes = bytes(self.audio_buffer[:self.frame_size_bytes])
            self.audio_buffer = self.audio_buffer[self.frame_size_bytes:]

            # Convert bytes to float32 tensor
            audio_array = np.frombuffer(frame_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            tensor_chunk = torch.from_numpy(audio_array)

            # Check for speech using VAD iterator
            speech_dict = self.vad_iterator(tensor_chunk)
            
            if speech_dict:
                if 'start' in speech_dict:
                    self.is_speaking = True
                    self.current_speech_segment = bytearray(frame_bytes)
                if 'end' in speech_dict and self.is_speaking:
                    self.is_speaking = False
                    self.current_speech_segment.extend(frame_bytes)
                    
                    # If the segment is long enough, save it
                    if len(self.current_speech_segment) > (self.sample_rate * 2 * 0.5):
                        completed_segments.append(bytes(self.current_speech_segment))
                    self.current_speech_segment = bytearray()
            elif self.is_speaking:
                self.current_speech_segment.extend(frame_bytes)

        return completed_segments
