# 🎬 ReFlow Studio (v0.4)
### *Local AI Studio: Universal Dubbing, Visual Censorship & Lip-Sync*

![License](https://img.shields.io/badge/license-MIT-6C5CE7)
![Release](https://img.shields.io/badge/version-0.4--beta-indigo)
![Engine](https://img.shields.io/badge/Engine-MuseTalk-purple)
![Platform](https://img.shields.io/badge/platform-Windows-0078D4)
![AI](https://img.shields.io/badge/AI--Engine-Local--Only-success)

**ReFlow Studio** is a powerhouse desktop suite designed to make global content accessible and family-friendly. By combining state-of-the-art **Whisper** (ASR), **XTTS** (Dubbing), **NudeNet** (Censorship), and **MuseTalk** (Lip-Sync), ReFlow allows you to localize videos entirely on your own hardware.

---

## ✨ Core Modules

### 👄 Cinema-Grade Lip Sync (NEW)
* **MuseTalk Integration:** Uses a Generative Adversarial Network (GAN) to sync lips at 256x256 resolution.
* **Hindi BBox Shift:** A proprietary algorithm (`bbox_shift`) that adjusts mouth positioning for fast-paced Indian languages.
* **Auto-FPS Fix:** Automatically standardizes input videos to 25 FPS to ensure perfect timing.

### 🎙️ AI Dubbing Engine
* **Neural Transcription:** Powered by **OpenAI Whisper** for near-perfect accuracy.
* **Voice Cloning (XTTS v2):** Generates natural, emotive speech that matches the original speaker's tone.
* **Docu-Mix Technology:** Professional-grade audio ducking—keep the background track while the AI voice takes the lead.

### 🛡️ Smart Safety Suite
* **Visual Shield (NudeNet):** Real-time frame analysis to blur NSFW content or gore.
* **Dynamic Audio Bleeping:** Automatically detects and replaces profanity with silence/bleeps.

---

## 📥 Getting Started

### 📦 Option 1: Windows Installer (Easy)
Our **Split Installer** handles the AI model weights by breaking them into manageable chunks.
1. Download `ReFlow_Setup_v0.4.exe` and all `.bin` files from the [Releases Page](https://github.com/ananta-sj/ReFlow-Studio/releases).
2. Ensure all files are in the same folder.
3. Run the `.exe` and follow the setup wizard.

### 🛠️ Option 2: Developer Setup (Source)

**Phase 1: The App**
```bash
git clone [https://github.com/ananta-sj/ReFlow-Studio.git](https://github.com/ananta-sj/ReFlow-Studio.git)
```
```bash
cd ReFlow-Studio
```
```bash
pip install -r requirements.txt
```

**Phase 2: MuseTalk**
```bash
conda create -n musetalk python=3.10
```
```bash
conda activate musetalk
```
```bash
python main.py
```

**On first run, ReFlow will ask you to locate your musetalk python executable. Point it to your conda environment.**

### **Block 5: Tech Stack**

## 🛠️ The Tech Stack
* **UI Framework:** CustomTkinter (Modern High-DPI UI)
* **Orchestration:** Python `subprocess` (Bridge Architecture)
* **Processing:** FFmpeg (Hardware accelerated)
* **AI Models:** * **Lip Sync:** MuseTalk (TMElyralab)
  * **ASR:** OpenAI Whisper
  * **TTS:** Coqui XTTS v2
  * **Vision:** NudeNet

## 🎨 Interface
| Light Theme | Dark Theme |
| :---: | :---: |
| ![Light Mode](assets/screenshot_light.png) | ![Dark Mode](assets/screenshot_dark.png) |

---

## 🤝 Contributing
ReFlow is an open-source project. 

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License
Distributed under the **MIT License**. See `LICENSE` for more information.

---
*Created with ❤️ by the ReFlow AI Team.*