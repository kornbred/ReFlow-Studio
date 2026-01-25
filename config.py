import os
import torch

# --- 1. PROJECT ROOT ---
# This automatically finds where this file is, so it works on any PC
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- 2. KEY DIRECTORIES ---
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
MODELS_DIR = os.path.join(ROOT_DIR, "models")
CORE_DIR   = os.path.join(ROOT_DIR, "core")

# Input/Output
INPUT_DIR  = os.path.join(ASSETS_DIR, "inputs")
OUTPUT_DIR = os.path.join(ASSETS_DIR, "outputs")
TEMP_DIR   = os.path.join(ASSETS_DIR, "temp")

# --- 3. MODEL PATHS (We will fill these later) ---
RVC_MODELS_DIR = os.path.join(MODELS_DIR, "rvc")
MUSETALK_MODELS_DIR = os.path.join(MODELS_DIR, "musetalk")

# --- 4. DEVICE SETTINGS ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"⚙️  CONFIGURATION LOADED | Root: {ROOT_DIR} | Device: {DEVICE}")

# Create temp dir if it doesn't exist (failsafe)
os.makedirs(TEMP_DIR, exist_ok=True)