import os
import cv2
import torch
import numpy as np
from gfpgan import GFPGANer
from tqdm import tqdm
import shutil

class FaceEnhancer:
    def __init__(self, device='cuda'):
        self.device = device
        self.model_path = os.path.join(os.getcwd(), "models", "enhancer", "GFPGANv1.4.pth")
        
        # Auto-Download Model
        if not os.path.exists(self.model_path):
            print("[ENHANCER] 📥 Downloading GFPGAN Model...")
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            url = "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth"
            torch.hub.download_url_to_file(url, self.model_path)

        print("[ENHANCER] ⏳ Loading GFPGAN Engine...")
        self.restorer = GFPGANer(
            model_path=self.model_path,
            upscale=1,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=None,
            device=self.device
        )

    def enhance(self, video_path, output_path):
        print(f"[ENHANCER] 💎 Enhancing Face Details in {os.path.basename(video_path)}...")
        
        # Open Video
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Setup Output
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Process Frames
        pbar = tqdm(total=total_frames, unit='frame', desc="Enhancing")
        
        while True:
            ret, frame = cap.read()
            if not ret: break

            # Enhance Face
            # cropped_faces, restored_faces, restored_img
            _, _, restored_img = self.restorer.enhance(
                frame,
                has_aligned=False,
                only_center_face=False,
                paste_back=True,
                weight=0.5 # 0.5 = Balanced (Natural), 1.0 = Artificial
            )

            # Write Frame
            out.write(restored_img)
            pbar.update(1)

        cap.release()
        out.release()
        pbar.close()
        
        print(f"[ENHANCER] ✅ Restoration Complete.")
        return output_path