import os
import sys
import torch

# Add project root to path to ensure we can find config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

class TTSHandler:
    def __init__(self):
        print("\n[TTS] ⏳ Initializing XTTS Pipeline...")
        
        # 1. Define Model Path
        self.model_path = os.path.join(config.MODELS_DIR, "xtts", "default")
        self.config_path = os.path.join(self.model_path, "config.json")
        
        # 2. Check if files exist
        if not os.path.exists(self.model_path) or not os.path.exists(self.config_path):
            print(f"[TTS] ❌ CRITICAL ERROR: Model files not found!")
            print(f"      Expected path: {self.model_path}")
            sys.exit(1)

        print(f"[TTS] 📂 Loading model from: {self.model_path}")

        try:
            from TTS.api import TTS
            # Force load with explicit paths
            self.tts = TTS(
                model_path=self.model_path,
                config_path=self.config_path,
                progress_bar=True,
                gpu=True
            ).to(config.DEVICE)
            print("[TTS] ✅ Model Loaded Successfully on GPU!")
            
        except Exception as e:
            print(f"[TTS] ❌ Model Load Failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def generate_audio(self, text, output_path, language="en", reference_audio=None):
        """
        Generates audio using XTTS.
        Prioritizes 'reference.wav' in the assets folder to prevent robotic voice.
        """
        if not self.tts:
            print("[ERROR] TTS Model not initialized.")
            return

        # --- SMART REFERENCE SELECTOR ---
        # 1. If a specific reference is passed, use it.
        # 2. If not, look for 'reference.wav' in the assets folder (User Custom).
        # 3. If that's missing, use the default sample (Robotic fallback).
        
        custom_ref_path = r"D:\New folder\Reflow-Studio\assets\reference.wav"
        default_sample = os.path.join(self.model_path, "samples", "en_sample.wav")

        if reference_audio and os.path.exists(reference_audio):
            speaker_wav = reference_audio
        elif os.path.exists(custom_ref_path):
            print(f"[TTS] 🎭 Using Custom Emotion Reference: {os.path.basename(custom_ref_path)}")
            speaker_wav = custom_ref_path
        else:
            print("[TTS] ⚠️ No custom reference found. Using generic default (May sound robotic).")
            print(f"       👉 Tip: Put a 10s voice clip named 'reference.wav' in {os.path.dirname(custom_ref_path)}")
            speaker_wav = default_sample

        print(f"[TTS] 🎙️ Generating ({language}): {text[:30]}...")
        
        try:
            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=speaker_wav,
                language=language,
                split_sentences=True,
                temperature=0.75,  # 0.75 = Good balance of emotion and stability
                speed=1.0          # We keep this 1.0 because Pipeline handles speed-up now
            )
            print(f"[TTS] 💾 Saved to: {output_path}")
            
        except Exception as e:
            print(f"[TTS] ❌ Generation Failed: {e}")

if __name__ == "__main__":
    handler = TTSHandler()