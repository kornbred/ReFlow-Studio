import os
import requests
import zipfile
import shutil
from tqdm import tqdm

class ModelManager:
    def __init__(self):
        self.root_dir = r"D:\New folder\Reflow-Studio"
        self.weights_dir = os.path.join(self.root_dir, "models", "rvc", "weights")
        self.temp_dir = os.path.join(self.root_dir, "temp", "downloads")
        os.makedirs(self.weights_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def download_file(self, url):
        # --- AUTO-FIX HUGGINGFACE LINKS ---
        if "huggingface.co" in url and "/blob/" in url:
            print("[MANAGER] Detected HuggingFace 'blob' link. Converting to direct download...")
            url = url.replace("/blob/", "/resolve/")
        
        local_filename = url.split('/')[-1].split('?')[0] # Clean URL params
        if not local_filename: local_filename = "downloaded_model.zip"
        path = os.path.join(self.temp_dir, local_filename)

        print(f"[DOWNLOAD] Starting: {local_filename}")
        
        # Headers to look like a browser
        headers = {'User-Agent': 'Mozilla/5.0'}

        # Stream download
        try:
            with requests.get(url, stream=True, headers=headers) as r:
                r.raise_for_status()
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)
        except Exception as e:
            raise Exception(f"Network Error: {str(e)}")
        
        return path

    def install_model(self, url):
        try:
            # 1. Download
            file_path = self.download_file(url)
            
            # 2. Extract or Move
            installed_names = []
            
            if file_path.endswith(".zip"):
                print("[INSTALL] Extracting archive...")
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(self.temp_dir)
                except zipfile.BadZipFile:
                    return "❌ Error: The downloaded file is not a valid ZIP. (Did the link redirect?)"

                # Hunt for .pth files
                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        if file.endswith(".pth") and "G_" not in file and "D_" not in file:
                            src = os.path.join(root, file)
                            dst = os.path.join(self.weights_dir, file)
                            shutil.move(src, dst)
                            installed_names.append(file)
            
            elif file_path.endswith(".pth"):
                print("[INSTALL] Installing single model...")
                dst = os.path.join(self.weights_dir, os.path.basename(file_path))
                shutil.move(file_path, dst)
                installed_names.append(os.path.basename(file_path))
            
            else:
                return "❌ Error: Link must end in .zip or .pth"

            # Cleanup
            try:
                for f in os.listdir(self.temp_dir):
                    p = os.path.join(self.temp_dir, f)
                    if os.path.isfile(p): os.remove(p)
                    elif os.path.isdir(p): shutil.rmtree(p)
            except: pass

            if not installed_names:
                return "⚠️ Downloaded, but no valid .pth model found inside."
            
            return f"✅ Installed: {', '.join(installed_names)}"

        except Exception as e:
            return f"❌ Installation Failed: {str(e)}"