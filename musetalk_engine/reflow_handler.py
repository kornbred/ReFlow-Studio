import os
import argparse
import subprocess
import sys
import yaml

def run_musetalk(video_path, audio_path, output_path, bbox_shift=0):
    # 1. DYNAMIC PATHS (The "Self-Aware" Fix)
    # The handler uses its OWN python (the one running it).
    # Since main.py launches this using the specific env python, sys.executable IS the correct python.
    engine_python = sys.executable 
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Setup Paths (Force forward slashes for cross-platform safety)
    video_path = os.path.abspath(video_path).replace("\\", "/")
    audio_path = os.path.abspath(audio_path).replace("\\", "/")
    output_path = os.path.abspath(output_path).replace("\\", "/")
    
    # Define Model Paths relative to the script location
    unet_config_path = os.path.join(current_dir, "models", "musetalk", "config.json").replace("\\", "/")
    unet_model_path = os.path.join(current_dir, "models", "musetalk", "pytorch_model.bin").replace("\\", "/")
    whisper_root = os.path.join(current_dir, "models", "whisper").replace("\\", "/")

    # 3. Config with TUNABLE BBOX_SHIFT
    temp_config_path = os.path.join(current_dir, "configs", "inference", "temp_job.yaml").replace("\\", "/")
    job_config = {
        "task_0": {
            "video_path": video_path,
            "audio_path": audio_path,
            "bbox_shift": int(bbox_shift)
        }
    }
    
    os.makedirs(os.path.dirname(temp_config_path), exist_ok=True)
    with open(temp_config_path, 'w', encoding='utf-8') as f:
        yaml.dump(job_config, f)

    # 4. Environment (UTF-8 Fix)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    # 5. Build Command
    cmd = [
        engine_python, "-m", "scripts.inference",
        "--inference_config", temp_config_path, 
        "--result_dir", output_path,
        "--unet_config", unet_config_path,
        "--unet_model_path", unet_model_path,
        "--whisper_dir", whisper_root
    ]

    print(f"[Handler] Launching MuseTalk (bbox_shift={bbox_shift})...")
    print(f"[Handler] Using Engine Python: {engine_python}")

    # 6. Execute
    try:
        result = subprocess.run(
            cmd, 
            cwd=current_dir, 
            env=env, 
            check=True,
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )
        # Sanitize logs for cleaner output
        clean_log = result.stdout.encode('ascii', 'ignore').decode('ascii')
        print("[Handler] STDOUT:", clean_log)
        return True

    except subprocess.CalledProcessError as e:
        print(f"[Handler] ENGINE CRASHED!")
        err_msg = e.stderr if e.stderr else "No error log."
        clean_err = err_msg.encode('ascii', 'ignore').decode('ascii')
        print(f"[Handler] Error Log:\n{clean_err}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--output", default="./results")
    parser.add_argument("--bbox_shift", default=0, type=int)
    args = parser.parse_args()
    
    run_musetalk(args.video, args.audio, args.output, args.bbox_shift)