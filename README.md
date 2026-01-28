<div align="center">

# 🎙️ Reflow Studio v0.5.2
### AI-Powered Neural Dubbing & Lip-Sync Workstation

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Gradio](https://img.shields.io/badge/UI-Gradio-FF7C00?style=for-the-badge&logo=gradio&logoColor=white)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

<br/>

<img src="assets\files\LOGO_ICON.png" width="100" alt="Reflow Studio Demo">

<br/>

**Reflow Studio** is a local, privacy-focused AI workstation for video dubbing, voice cloning, and lip synchronization. It combines state-of-the-art models (**RVC**, **Wav2Lip**, **GFPGAN**) into a single, cohesive "Cyberpunk" interface designed for creators.

[Report Bug](https://github.com/ananta-sj/Reflow-Studio/issues) · [Request Feature](https://github.com/ananta-sj/Reflow-Studio/issues)

</div>


## 🎞️ Trailer (v0.5.2)

<div align="center">
  <video src="https://github.com/user-attachments/assets/9297d024-b4ea-4577-adde-5174235c2056" width="80%" controls></video>
</div>


---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🤖 Neural Voice Cloning** | Clone voices instantly using **RVC (Retrieval-based Voice Conversion)**. |
| **👄 Wav2Lip Sync** | Automatically synchronize lip movements to match the new dubbed audio. |
| **👁️ Face Enhancement** | Restore face details lost during lip-sync using **GFPGAN** & **CodeFormer**. |
| **🎬 Auto-Dubbing** | (Coming Soon) End-to-end video-to-video translation and dubbing. |
| **🛡️ Vision Meter** | Real-time content filtering and "Family Mode" safety checks. |
| **🚀 Portable Runtime** | Runs locally without complex installation (See Releases). |

---

## 🎞️ Demo (UI)

> *The following is a raw view from Reflow Studio v0.5.2.*

<div align="center">
  <video src="https://github.com/user-attachments/assets/f0f7a2d6-8159-4bd2-9742-de48ff652a1d" width="80%" controls></video>
</div>

---

## 🎞️ Test Sample

> *The following is a raw input and output from Reflow Studio v0.5.2.*

| **Original Input** | **Reflow Output** |
| :---: | :---: |
| <video src="https://github.com/user-attachments/assets/b144775c-947f-423a-a328-15b576f53c04" width="100%" controls></video> | <video src="https://github.com/user-attachments/assets/f89e78e1-c5b7-4e09-8843-768e21e1bfca" width="100%" controls></video> |

---

## 🛠️ Installation

### Option A: The One-Click Portable App (Recommended)
No coding required. Just download, extract, and run.
1. Go to the [**Releases**](https://github.com/ananta-sj/Reflow-Studio/releases) page.
2. Download `Reflow_Portable.part01 - part05`.
3. Extract the files.
4. Double-click **`Run_Reflow.bat`**.

### Option B: Developer Setup (Source)
If you want to modify the code or run it in your own Python environment.

**Prerequisites:**
* Python 3.10
* NVIDIA GPU (Recommended) with CUDA 11.8+

```bash
# 1. Clone the repo
git clone [https://github.com/ananta-sj/Reflow-Studio.git](https://github.com/ananta-sj//Reflow-Studio.git)
cd Reflow-Studio

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Install PyTorch (CUDA 11.8)
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu118](https://download.pytorch.org/whl/cu118)

# 4. Install dependencies
pip install -r requirements.txt

# 5. 📥 Download AI Models (Critical Step): Because AI models are too large for GitHub, you must run this script once to fetch them:
python setup_models.py

# 6. Run the Studio
python studio_gui_v0.5.py
```

### **Part 3: Usage, Structure & Footer**

## 🎛️ Usage Guide

### 1. Main Dashboard
* **Voice Cast:** Select from installed RVC models or use the default `CLONED_USER`.
* **Mixer & Video:**
    * `PRESERVE MUSIC/SFX`: Keeps the background audio while replacing vocals.
    * `ENABLE WAV2LIP`: Forces the video mouth to move with the new audio.
    * `ENHANCE FACE`: Upscales the face area to fix blurriness (slower but higher quality).
* **Vision Meter:** Adjusts the safety filter sensitivity.

### 2. Script Tab
* Auto-transcribe your video or manually paste a script to guide the TTS/Dubbing engine.

### 3. Model Manager
* Paste a HuggingFace/Drive link to download new RVC voice models directly into the app.

---

## 📂 Project Structure
```
Reflow-Studio/
├── core/                  # Backend logic (Pipeline, Model Managers)
├── models/                # AI Weights (RVC, GFPGAN, etc.)
│   ├── rvc/
│   └── gfpgan/
├── studio_gui_v0.5.2.py     # Main Gradio Interface Entry Point
├── requirements.txt       # Python Dependencies
└── README.md              # Documentation
```
## 🤝 Acknowledgements

This project stands on the shoulders of giants. Special thanks to the open-source community:

* **[RVC-Project](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)** - The core voice conversion engine.
* **[Wav2Lip](https://github.com/Rudrabha/Wav2Lip)** - State-of-the-art lip synchronization.
* **[GFPGAN](https://github.com/TencentARC/GFPGAN)** - Face restoration.
* **[Gradio](https://gradio.app/)** - The beautiful web UI framework.

---

<div align="center">

**Reflow Studio** © 2026
Built with ❤️ by Reflow Studio Team

</div>