import PyInstaller.__main__
import os
import shutil
import time
from PyInstaller.utils.hooks import collect_data_files

# --- CONFIGURATION ---
APP_NAME = "ReFlow"
MAIN_FILE = "main.py"
ICON_FILE = os.path.join("assets", "icon.ico")
SPLASH_FILE = os.path.join("assets", "splash.png")

# 1. FORCE KILL OLD PROCESSES
print(f"--- STARTING BUILD: {APP_NAME} ---")
os.system(f"taskkill /F /IM {APP_NAME}.exe 2>nul")
time.sleep(2)

# 2. CLEANUP
if os.path.exists("dist"): shutil.rmtree("dist")
if os.path.exists("build"): shutil.rmtree("build")

# 3. COLLECT DATA
print("   > Collecting dependencies...")
profanity_datas = collect_data_files('better_profanity')
data_args = []
for source, dest in profanity_datas:
    data_args.append(f'--add-data={source};{dest}')

# 4. BUILD COMMAND
cmd = [
    MAIN_FILE,
    f'--name={APP_NAME}',
    '--onedir',
    '--windowed',
    '--clean',
    '--noconfirm',
]

if os.path.exists(ICON_FILE): cmd.append(f'--icon={ICON_FILE}')
if os.path.exists(SPLASH_FILE): cmd.append(f'--splash={SPLASH_FILE}')

cmd.extend(data_args)

# Exclude heavy ML libraries from the UI EXE
cmd.extend([
    '--hidden-import=better_profanity',
    '--exclude-module=torch',
    '--exclude-module=transformers',
    '--exclude-module=TTS',
    '--exclude-module=matplotlib',
    '--exclude-module=ipython',
])

PyInstaller.__main__.run(cmd)

# 5. POST-BUILD COPYING
print("\n--- POST-BUILD COPYING ---")
dist_folder = os.path.join("dist", APP_NAME)
os.makedirs(os.path.join(dist_folder, "outputs"), exist_ok=True)

if os.path.exists("ffmpeg.exe"):
    shutil.copy("ffmpeg.exe", os.path.join(dist_folder, "ffmpeg.exe"))

# CRITICAL: Copy the Engine
print("   > Copying AI Engine...")
src_engine = "engine"
dst_engine = os.path.join(dist_folder, "engine")

if os.path.exists(src_engine):
    # Copy engine but SKIP git files and cache
    shutil.copytree(src_engine, dst_engine, dirs_exist_ok=True, 
                    ignore=shutil.ignore_patterns("__pycache__", "*.git", "checkpoints")) 
    
    # ⚠️ MANUALLY COPY CHECKPOINTS (Optional for Speed)
    # If you want the build to include the 3GB models, remove "checkpoints" from the ignore list above.
    # Otherwise, you must manually copy 'checkpoints' to dist/ReFlow/engine/checkpoints after build.
    print("     [OK] Engine structure copied.")
else:
    print("     [ERROR] Engine folder not found!")

print(f"\nSUCCESS! Build is ready at: {os.path.abspath(dist_folder)}")