import os
import subprocess
import sys
import logging
import shutil

logging.basicConfig(level=logging.INFO)

class LipSyncHandler:
    def __init__(self):
        self.root_dir = r"D:\New folder\Reflow-Studio"
        self.wav2lip_dir = os.path.join(self.root_dir, "core", "Wav2Lip")
        self.checkpoints_dir = os.path.join(self.root_dir, "models", "lipsync")
        
        # Smart Search for Model
        self.model_path = None
        target_name = "wav2lip_gan.pth"
        
        if os.path.exists(self.checkpoints_dir):
            for root, dirs, files in os.walk(self.checkpoints_dir):
                for file in files:
                    if file.lower() == target_name.lower():
                        self.model_path = os.path.join(root, file)
                        break
                if self.model_path: break
        
        if not self.model_path:
            self.model_path = os.path.join(self.checkpoints_dir, target_name)

    def execute(self, video_path, audio_path, output_path):
        if not os.path.exists(self.model_path):
            print(f"[LIPSYNC] ❌ CRITICAL: Model file is missing.")
            return None

        print("[LIPSYNC] ⏳ Loading Wav2Lip Engine...")
        
        # 1. SETUP LOCAL FILENAMES (No Spaces!)
        local_video = "temp_input.mp4"
        local_audio = "temp_input.wav"
        local_output = "temp_output.mp4"

        full_video_path = os.path.join(self.wav2lip_dir, local_video)
        full_audio_path = os.path.join(self.wav2lip_dir, local_audio)
        full_output_path = os.path.join(self.wav2lip_dir, local_output)
        
        # Cleanup
        if os.path.exists(full_output_path): os.remove(full_output_path)
        if os.path.exists(full_video_path): os.remove(full_video_path)
        if os.path.exists(full_audio_path): os.remove(full_audio_path)

        # 2. COPY & PREPARE AUDIO
        shutil.copy(audio_path, full_audio_path)
        
        # 3. COPY & PREPARE VIDEO (Try 720p Optimize)
        print("[LIPSYNC] 🛠️ Optimizing video for AI (720p)...")
        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path,
                '-vf', 'scale=-2:720', 
                '-r', '25',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-an',
                full_video_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print("[LIPSYNC] 🔄 Fallback: Using original video directly.")
            shutil.copy(video_path, full_video_path)

        # 4. RUN INFERENCE (With Padding Fix)
        inference_script = "inference.py"
        
        cmd = [
            sys.executable, inference_script,
            "--checkpoint_path", self.model_path,
            "--face", local_video, 
            "--audio", local_audio,
            "--outfile", local_output,
            "--nosmooth",
            "--resize_factor", "1",
            "--pads", "0", "20", "0", "0"  # <--- THE MAGIC FIX (Top Bottom Left Right)
        ]

        try:
            print("[LIPSYNC] 🚀 Starting AI Processing (Aggressive Mode)...")
            process = subprocess.run(
                cmd, 
                cwd=self.wav2lip_dir,
                capture_output=True,
                text=True
            )
            
            # 5. RETRIEVE RESULT
            if os.path.exists(full_output_path) and os.path.getsize(full_output_path) > 1000:
                print(f"[LIPSYNC] ✅ Success! Moving file...")
                if os.path.exists(output_path): os.remove(output_path)
                shutil.move(full_output_path, output_path)
                
                # Cleanup
                if os.path.exists(full_video_path): os.remove(full_video_path)
                if os.path.exists(full_audio_path): os.remove(full_audio_path)
                return output_path
            else:
                print("\n" + "!"*40)
                print("[LIPSYNC] ❌ CRASH DETECTED")
                print("ERROR LOG FROM ENGINE:")
                print(process.stderr)
                print("!"*40 + "\n")
                return None

        except Exception as e:
            print(f"[LIPSYNC] ❌ Execution Error: {str(e)}")
            return None