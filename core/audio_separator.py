import os
import subprocess
import shutil
import logging

logging.basicConfig(level=logging.INFO)

class AudioSeparator:
    def __init__(self):
        self.root_dir = r"D:\New folder\Reflow-Studio"
        self.temp_dir = os.path.join(self.root_dir, "temp")
        self.models_dir = os.path.join(self.root_dir, "models", "demucs")
        os.makedirs(self.models_dir, exist_ok=True)

    def separate(self, input_audio_path):
        """
        Splits audio into 'vocals.wav' and 'background.wav'.
        Returns: (vocals_path, background_path)
        """
        print(f"[SEPARATOR] ✂️ Splitting Audio: {os.path.basename(input_audio_path)}")
        
        # We use the 'htdemucs' model (fast and good quality)
        cmd = [
            "demucs",
            "--two-stems=vocals", # Only split into vocals vs others
            "-n", "htdemucs",     # Model Name
            "--out", self.temp_dir,
            input_audio_path
        ]
        
        try:
            subprocess.run(cmd, check=True)
            
            # Demucs saves files in a specific nested folder structure:
            # temp/htdemucs/{filename}/vocals.wav
            filename = os.path.splitext(os.path.basename(input_audio_path))[0]
            output_folder = os.path.join(self.temp_dir, "htdemucs", filename)
            
            generated_vocals = os.path.join(output_folder, "vocals.wav")
            generated_bg = os.path.join(output_folder, "no_vocals.wav")
            
            # We move them to our main temp folder for easier access
            final_vocals = os.path.join(self.temp_dir, "clean_vocals.wav")
            final_bg = os.path.join(self.temp_dir, "background.wav")
            
            if os.path.exists(generated_vocals):
                shutil.move(generated_vocals, final_vocals)
                shutil.move(generated_bg, final_bg)
                
                # Cleanup the demucs folder
                shutil.rmtree(os.path.join(self.temp_dir, "htdemucs"), ignore_errors=True)
                
                print("[SEPARATOR] ✅ Split Complete.")
                return final_vocals, final_bg
            else:
                print("[SEPARATOR] ❌ Extraction failed (Files not found).")
                return None, None

        except Exception as e:
            print(f"[SEPARATOR] ❌ Critical Error: {e}")
            return None, None