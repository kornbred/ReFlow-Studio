import os
import requests
import sys

# Try to import tqdm for progress bars, strictly optional
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# --- CONFIGURATION: The Missing Brains ---
# Format: "Local Path": "Download URL"
REQUIRED_MODELS = {
    # 1. Wav2Lip Model (The Lip Sync Brain)
    "models/wav2lip_gan.pth": "https://huggingface.co/camenduru/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth",
    
    # 2. GFPGAN Model (The Face Enhancer)
    # Note: Standard GFPGAN structure usually puts weights in 'gfpgan/weights' or just 'gfpgan'
    # Adjust 'gfpgan/GFPGANv1.4.pth' to match where your code expects it.
    "gfpgan/weights/GFPGANv1.4.pth": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
    
    # 3. Face Detection (S3FD) - Often needed by Wav2Lip
    "face_detection/detection/sfd/s3fd.pth": "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth"
}

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        print(f"✅ Found: {dest_path}")
        return

    print(f"⬇️ Downloading: {os.path.basename(dest_path)}...")
    
    # Create folder if missing
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest_path, 'wb') as f:
            if tqdm:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                        pbar.update(len(chunk))
            else:
                # Fallback without progress bar
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
                    
        print(f"   Success.")
        
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        # Clean up partial file
        if os.path.exists(dest_path):
            os.remove(dest_path)

def main():
    print("--- REFLOW STUDIO: MODEL SETUP ---")
    print("Checking for required AI models...")
    
    for local_path, url in REQUIRED_MODELS.items():
        # Handle path differences across OS
        full_path = os.path.normpath(local_path)
        download_file(url, full_path)
        
    print("\n✅ All models are ready. You can now run the Studio!")

if __name__ == "__main__":
    main()