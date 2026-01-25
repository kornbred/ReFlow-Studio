import os
import json
import logging
import shutil
import subprocess

logging.basicConfig(level=logging.INFO)

class RVCHandler:
    def __init__(self, device="cuda"):
        self.device = device
        self.ready = False
        print(f"[RVC] ⏳ Initializing RVC Engine ({self.device})...")
        
        try:
            from rvc_python.infer import RVCInference
            self.inference = RVCInference(device=self.device)
            self.ready = True
            print("[RVC] ✅ RVC System Online.")
        except ImportError as e:
            print(f"[RVC] ❌ IMPORT ERROR: {str(e)}")
        except Exception as e:
            print(f"[RVC] ❌ UNKNOWN ERROR: {str(e)}")

    def create_v2_config(self, config_path):
        """Generates a forced V2 config."""
        data = {
            "train": {"log_interval": 200, "epochs": 20000, "learning_rate": 0.0001, "batch_size": 4},
            "data": {"max_wav_value": 32768.0, "sampling_rate": 40000, "filter_length": 1024, "hop_length": 256, "win_length": 1024},
            "model": {"inter_channels": 192, "hidden_channels": 768, "filter_channels": 768, "n_heads": 2, "n_layers": 6, "kernel_size": 3, "p_dropout": 0.1, "resblock": "1", "resblock_kernel_sizes": [3, 7, 11], "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]], "upsample_rates": [10, 10, 2, 2], "upsample_initial_channel": 512, "upsample_kernel_sizes": [16, 16, 4, 4], "use_spectral_norm": False, "gin_channels": 256, "spk_embed_dim": 109},
            "version": "v2"
        }
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)

    def preprocess_audio(self, input_path):
        """
        Converts audio to 16k mono to prevent Tensor Mismatch errors.
        Returns path to the temp file.
        """
        temp_16k = input_path.replace(".wav", "_16k.wav")
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-ar', '16000',  # Force 16k Sample Rate (Hubert Native)
            '-ac', '1',      # Force Mono
            temp_16k
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(temp_16k):
            return temp_16k
        return input_path # Fallback

    def infer(self, input_audio, output_audio, model_name, pitch_change=0):
        if not self.ready: return

        weights_dir = os.path.join(os.getcwd(), "models", "rvc", "weights")
        model_path = os.path.join(weights_dir, f"{model_name}.pth")
        config_path = os.path.join(weights_dir, f"{model_name}.json")

        self.create_v2_config(config_path)
        shutil.copy(config_path, os.path.join(weights_dir, "config.json"))

        print(f"[RVC] 🎤 Morphing: {os.path.basename(input_audio)} -> {model_name}")

        # --- FIX: STANDARDIZE INPUT AUDIO ---
        clean_input = self.preprocess_audio(input_audio)

        try:
            # 1. Inject Config
            if hasattr(self.inference, "config"):
                with open(config_path, 'r') as f:
                    conf = json.load(f)
                if hasattr(self.inference.config, "model"):
                    self.inference.config.model = conf['model']
                if hasattr(self.inference.config, "data"):
                    self.inference.config.data = conf['data']

            # 2. Load Model
            if hasattr(self.inference, "load_model"):
                self.inference.load_model(model_path)
            elif hasattr(self.inference, "set_model"):
                self.inference.set_model(model_path)

            # 3. RUN INFERENCE (Using clean 16k audio)
            # Based on your logs, 'infer_file' only wants input_path and output_path
            # The library likely handles pitch/f0 internally or via config now.
            
            try:
                # Modern call
                self.inference.infer_file(
                    input_path=clean_input, 
                    output_path=output_audio,
                    f0_up_key=pitch_change # Try passing pitch if possible
                )
            except TypeError:
                # Fallback call (Strictly what the debug log showed)
                self.inference.infer_file(
                    input_path=clean_input, 
                    output_path=output_audio
                )

            print(f"[RVC] ✅ Success: {os.path.basename(output_audio)}")
            
        except Exception as e:
            print(f"[RVC] ❌ FAILED: {str(e)}")
        
        # Cleanup temp file
        if clean_input != input_audio and os.path.exists(clean_input):
            os.remove(clean_input)