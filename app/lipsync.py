import os
import subprocess

# ==============================================================================
ENGINE_PYTHON_PATH = r"C:\Users\19shr\miniconda3\envs\reflow_engine\python.exe" 
# ==============================================================================

def run_retalking(face_video, audio_track, output_path):
    # 1. Setup Paths
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script_dir)
    engine_dir = os.path.join(project_root, "engine")
    engine_script = "inference.py"

    # 2. Check if the path was updated
    if "PASTE_YOUR_PATH_HERE" in ENGINE_PYTHON_PATH:
         return "❌ Setup Error: You forgot to paste the Python Path in app/lipsync.py!"
         
    if not os.path.exists(ENGINE_PYTHON_PATH):
        return f"❌ Error: Could not find the Engine Python at: {ENGINE_PYTHON_PATH}"

    # 3. The Command
    # We use the "Old Brain" (ENGINE_PYTHON_PATH) to run the script
    command = [
        ENGINE_PYTHON_PATH, 
        engine_script,
        "--face", os.path.abspath(face_video),
        "--audio", os.path.abspath(audio_track),
        "--outfile", os.path.abspath(output_path)
    ]

    print(f"🚀 Sending job to AI Engine...")
    print(f"   Using Python: {ENGINE_PYTHON_PATH}")
    
    try:
        # 4. Run the command inside the 'engine' folder
        process = subprocess.Popen(
            command,
            cwd=engine_dir, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        # Print logs so you can see it working
        for line in process.stdout:
            print(f"   [ENGINE] {line.strip()}")

        process.wait()

        if process.returncode == 0:
            return f"✅ Success! Output saved to: {output_path}"
        else:
            return "❌ Engine failed. Check logs above."

    except Exception as e:
        return f"❌ System Error: {str(e)}"