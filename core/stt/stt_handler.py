import torch
import gc
from faster_whisper import WhisperModel

class STTHandler:
    def __init__(self, device="cpu"): 
        # FORCE CPU to prevent DLL crash with OnnxRuntime
        self.device = "cpu"
        self.model_size = "medium" 
        self.compute_type = "int8" 
        
        print(f"[STT] ⏳ Loading Whisper Model ({self.model_size}) on CPU [Safe Mode]...")
        try:
            self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        except Exception as e:
            print(f"[STT] ❌ Critical Error loading Whisper: {e}")
            raise e

    def transcribe(self, audio_path):
        # Beam size 5 gives better accuracy
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        
        result = []
        for segment in segments:
            result.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
        
        # Cleanup
        del self.model
        gc.collect()
        
        return result