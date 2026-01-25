import sys
import os
import json

# Add the 'core' folder to Python path so we can find stt_handler
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)

from stt.stt_handler import STTHandler

if __name__ == "__main__":
    video_path = sys.argv[1]
    json_output_path = sys.argv[2]

    print(f"[WORKER] 🛠️ Soldier started for: {video_path}")
    
    # We use CPU here to be 100% safe from GPU conflicts
    # Since this is a separate process, it won't crash the main app
    stt = STTHandler(device="cpu")
    transcript = stt.transcribe(video_path)
    
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, ensure_ascii=False, indent=4)
        
    print("[WORKER] ✅ Mission Complete. Saving JSON.")