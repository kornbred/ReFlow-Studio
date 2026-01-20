import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import os
import threading
import subprocess
import sys
import re
import glob
from collections import Counter
from settings import SettingsManager
import time

# --- SPLASH SCREEN CLOSER ---
try:
    import pyi_splash
    pyi_splash.update_text('UI Loaded...')
    pyi_splash.close()
except:
    pass

import json

# ==============================================================================
# ⚙️ DYNAMIC ENGINE CONFIGURATION
# ==============================================================================
ENGINE_ROOT = os.path.join(os.getcwd(), "musetalk_engine") # Relative to main.py
HANDLER_SCRIPT = os.path.join(ENGINE_ROOT, "reflow_handler.py")
CONFIG_FILE = "config.json"

def load_or_ask_config():
    """
    Checks for a saved config. If not found, prompts the user to locate
    the MuseTalk Python executable.
    """
    config = {}
    
    # 1. Try to load existing config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        except:
            pass
    
    # 2. Check if we have a valid python path
    musetalk_python = config.get("musetalk_python", "")
    
    if not musetalk_python or not os.path.exists(musetalk_python):
        print("[Setup] First time setup: Please locate the MuseTalk 'python.exe'")
        
        # Open a distinct dialog box
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        tk.messagebox.showinfo("ReFlow Setup", 
            "We need to link the AI Engine.\n\nPlease select the 'python.exe' inside your 'musetalk' environment folder.")
            
        musetalk_python = filedialog.askopenfilename(
            title="Select MuseTalk Python.exe",
            filetypes=[("Python Executable", "python.exe")]
        )
        root.destroy()
        
        if not musetalk_python:
            print("[Setup] Cancelled. Exiting.")
            sys.exit()
            
        # Save it for next time
        config["musetalk_python"] = musetalk_python
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
            
    return musetalk_python

# LOAD THE PATH DYNAMICALLY
MUSETALK_PYTHON = load_or_ask_config()
FFMPEG_EXE = os.path.join(os.path.dirname(MUSETALK_PYTHON), "Library", "bin", "ffmpeg.exe")

# ==============================================================================
# 🛠️ HELPER FUNCTIONS (The "Pro" Tools)
# ==============================================================================

def convert_to_25fps(video_path):
    """
    Takes any video and forces it to 25 FPS using the 'Good' FFmpeg.
    Returns the path to the new 25fps version.
    """
    print(f"[ReFlow] Checking video FPS: {video_path}")
    
    base, ext = os.path.splitext(video_path)
    # Avoid double converting if already named _25fps
    if base.endswith("_25fps"):
        return video_path

    output_path = f"{base}_25fps{ext}"
    
    # Fallback if specific ffmpeg not found
    exe_to_use = FFMPEG_EXE if os.path.exists(FFMPEG_EXE) else "ffmpeg"

    cmd = [
        exe_to_use, "-i", video_path, 
        "-r", "25", "-y", output_path
    ]
    
    print(f"[ReFlow] Auto-Converting to 25 FPS for Sync Stability...")
    try:
        # Run silently
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[ReFlow] Conversion Complete: {output_path}")
        return output_path
    except Exception as e:
        print(f"[ReFlow] WARNING: FPS Conversion failed ({e}). Using original.")
        return video_path

def call_musetalk_engine(video_path, audio_path, bbox_shift=0):
    """
    Calls the isolated MuseTalk environment to process the video.
    """
    shift_val = str(int(bbox_shift))

    cmd = [
        MUSETALK_PYTHON,   
        HANDLER_SCRIPT,    
        "--video", video_path,
        "--audio", audio_path,
        "--output", os.path.join(ENGINE_ROOT, "results"),
        "--bbox_shift", shift_val
    ]
    
    print(f"[ReFlow Bridge] Sending job to Engine...")
    print(f"   Video: {video_path}")
    print(f"   Audio: {audio_path}")
    print(f"   Shift: {shift_val}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=ENGINE_ROOT, 
            check=True,
            encoding='utf-8', 
            errors='replace'
        )
        print("[ReFlow Bridge] Engine Success!")
        return {"success": True, "logs": result.stdout}
        
    except subprocess.CalledProcessError as e:
        print(f"[ReFlow Bridge] Engine Failed!")
        err_log = e.stderr if e.stderr else "No error log."
        print(err_log.encode('ascii', 'ignore').decode('ascii'))
        return {"success": False, "error": err_log}

def pick_file(title="Select File", file_types=[("Video files", "*.mp4;*.avi;*.mov")]):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
    root.destroy()
    return file_path

def clean_repetitive_text(text):
    if not text: return ""
    phrases = re.split(r'[.,;।]+', text)
    phrases = [p.strip() for p in phrases if p.strip()]
    if not phrases: return text
    counts = Counter(phrases)
    cleaned_phrases = []
    seen = set()
    has_changed = False
    for p in phrases:
        if counts[p] > 3:
            if p not in seen:
                cleaned_phrases.append(p)
                seen.add(p)
                has_changed = True
        else:
            cleaned_phrases.append(p)
    if has_changed: return "। ".join(cleaned_phrases) + "।"
    return text

# ==============================================================================
# 🎨 THEME CONFIGURATION
# ==============================================================================
COLORS = {
    "bg_window":    ("#F2F5F8", "#0B0E14"),
    "bg_sidebar":   ("#FFFFFF", "#151923"),
    "card_bg":      ("#FFFFFF", "#1E2230"),
    "card_hover":   ("#F8FAFC", "#252A3A"),
    "text_main":    ("#1A1C23", "#FFFFFF"),
    "text_sub":     ("#64748B", "#94A3B8"),
    "accent":       ("#6366F1", "#6C5CE7"),
    "accent_hover": ("#4F46E5", "#5849C2"),
    "success":      ("#10B981", "#00C896"),
    "warning":      ("#F59E0B", "#FACC15"),
    "danger":       ("#EF4444", "#FF5252"),
    "border":       ("#E2E8F0", "#2A2F40"),
}

FONTS = {
    "display": ("Segoe UI", 28, "bold"),
    "h1":      ("Segoe UI", 20, "bold"),
    "h2":      ("Segoe UI", 14, "bold"),
    "body":    ("Segoe UI", 12),
    "small":   ("Segoe UI", 11),
    "badge":   ("Segoe UI", 9, "bold")
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- MODERN WIDGETS ---
class ModernSwitch(ctk.CTkSwitch):
    def __init__(self, parent, text, default=False, command=None):
        super().__init__(parent, text=text, 
                         font=FONTS["body"], 
                         text_color=COLORS["text_main"],
                         progress_color=COLORS["accent"],
                         button_color=COLORS["bg_window"],
                         button_hover_color=COLORS["bg_sidebar"],
                         fg_color=COLORS["border"],
                         border_width=0,
                         command=command) 
        if default: self.select()

class StatWidget(ctk.CTkFrame):
    def __init__(self, parent, label, value="0", icon="📊"):
        super().__init__(parent, fg_color=COLORS["card_bg"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        self.grid_columnconfigure(0, weight=1)
        self.lbl_icon = ctk.CTkLabel(self, text=icon, font=("Segoe UI", 16), text_color=COLORS["text_sub"])
        self.lbl_icon.grid(row=0, column=1, padx=15, pady=(10,0), sticky="ne")
        self.lbl_val = ctk.CTkLabel(self, text=value, font=FONTS["display"], text_color=COLORS["text_main"], anchor="w")
        self.lbl_val.grid(row=0, column=0, padx=15, pady=(10,0), sticky="nw")
        self.lbl_name = ctk.CTkLabel(self, text=label, font=FONTS["small"], text_color=COLORS["text_sub"], anchor="w")
        self.lbl_name.grid(row=1, column=0, padx=15, pady=(0,15), sticky="nw")

    def set_value(self, val):
        self.lbl_val.configure(text=str(val))

class JobCard(ctk.CTkFrame):
    def __init__(self, parent, index, filepath, status="Pending"):
        super().__init__(parent, fg_color=COLORS["card_bg"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        self.filepath = filepath
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.grid_columnconfigure(1, weight=1) 
        
        self.icon_bg = ctk.CTkFrame(self, width=46, height=46, corner_radius=14, fg_color=COLORS["bg_window"])
        self.icon_bg.grid(row=0, column=0, rowspan=2, padx=16, pady=16)
        ctk.CTkLabel(self.icon_bg, text="▶", font=("Arial", 14, "bold"), text_color=COLORS["accent"]).place(relx=0.5, rely=0.5, anchor="center")

        filename = os.path.basename(filepath)
        if len(filename) > 40: filename = filename[:37] + "..."
        self.lbl_title = ctk.CTkLabel(self, text=filename, font=FONTS["h2"], text_color=COLORS["text_main"], anchor="w")
        self.lbl_title.grid(row=0, column=1, padx=(0,10), pady=(16,0), sticky="ew")
        
        self.lbl_sub = ctk.CTkLabel(self, text="Waiting in queue...", font=FONTS["small"], text_color=COLORS["text_sub"], anchor="w")
        self.lbl_sub.grid(row=1, column=1, padx=(0,10), pady=(0,16), sticky="nsw")

        self.status_pill = ctk.CTkFrame(self, height=24, corner_radius=12, fg_color=COLORS["bg_window"])
        self.status_pill.grid(row=0, column=2, padx=20, pady=(18,0), sticky="ne")
        self.lbl_status = ctk.CTkLabel(self.status_pill, text=status.upper(), font=FONTS["badge"], text_color=COLORS["text_sub"])
        self.lbl_status.pack(padx=12, pady=2)

        self.progress = ctk.CTkProgressBar(self, height=3, corner_radius=0, progress_color=COLORS["success"], fg_color=COLORS["border"])
        self.progress.grid(row=2, column=0, columnspan=3, sticky="ew", padx=2, pady=(0,2))
        self.progress.set(0.0)

    def on_hover(self, event):
        self.configure(fg_color=COLORS["card_hover"], border_color=COLORS["accent"])
    def on_leave(self, event):
        self.configure(fg_color=COLORS["card_bg"], border_color=COLORS["border"])
    def set_status(self, status, color_key="gray"):
        self.lbl_sub.configure(text=status)
        self.lbl_status.configure(text=status.upper())
        colors = {"green": (COLORS["success"], "white"), "orange": (COLORS["warning"], "black"), "blue": (COLORS["accent"], "white"), "red": (COLORS["danger"], "white"), "purple": ("#8B5CF6", "white"), "gray": (COLORS["bg_window"], COLORS["text_sub"])}
        bg, txt = colors.get(color_key, colors["gray"])
        self.status_pill.configure(fg_color=bg)
        self.lbl_status.configure(text_color=txt)
    def set_progress(self, val):
        self.progress.set(val)

class ReFlowStudio(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        saved_theme = self.settings_manager.get("theme")
        ctk.set_appearance_mode(saved_theme)
        ctk.set_default_color_theme(self.settings_manager.get("color_theme"))
        
        self.title("ReFlow Studio v0.3.1 - MuseTalk Engine")
        self.geometry("1280x850")
        self.configure(fg_color=COLORS["bg_window"]) 
        
        self.queue_files = []
        self.queue_widgets = []
        self.is_processing = False
        self.stop_requested = False
        self.ai_whisper = None
        self.ai_tts = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=290, corner_radius=0, fg_color=COLORS["bg_sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.logo_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_box.pack(pady=(40,30), padx=30, fill="x")
        self.logo_box.pack_propagate(False)
        ctk.CTkLabel(self.logo_box, text="ReFlow.", font=("Poppins", 30, "bold"), text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(self.logo_box, text="AI STUDIO PRO", font=("Segoe UI", 10, "bold"), text_color=COLORS["accent"]).pack(anchor="w")

        self.settings_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.settings_frame.pack(fill="both", expand=True, padx=5)

        self.theme_switch = ctk.CTkSwitch(self.settings_frame, text="Dark Theme", command=self.toggle_theme, font=FONTS["body"], text_color=COLORS["text_main"], progress_color=COLORS["accent"])
        if saved_theme == "Dark": self.theme_switch.select()
        else: self.theme_switch.deselect(); self.theme_switch.configure(text="Light Theme")
        self.theme_switch.pack(pady=(0, 20), padx=20, anchor="w")

        self.add_group_header("PROCESS")
        self.combo_lang = ctk.CTkComboBox(self.settings_frame, values=["Hinglish", "Hindi", "English"], fg_color=COLORS["bg_window"], text_color=COLORS["text_main"], button_color=COLORS["border"], dropdown_fg_color=COLORS["bg_window"], height=35, command=self.save_language_pref) 
        saved_lang = self.settings_manager.get("language")
        if not saved_lang: saved_lang = "Hinglish"
        self.combo_lang.set(saved_lang)
        self.combo_lang.pack(fill="x", padx=20, pady=10)

        self.add_switch("AI Dubbing", True, self.settings_frame, "dub")
        self.add_switch("Visual Blur (NSFW)", False, self.settings_frame, "visual")
        self.add_switch("Burn Subtitles", True, self.settings_frame, "sub")
        self.add_switch("Censor Audio", True, self.settings_frame, "censor")
        self.add_switch("Docu-Mix Mode", False, self.settings_frame, "docu")
        
        self.chk_lipsync = ctk.BooleanVar(value=False)
        self.add_switch("AI Lip Sync (Beta)", False, self.settings_frame, "lipsync")

        self.add_group_header("FILTERS")
        self.entry_ignore = ctk.CTkEntry(self.settings_frame, placeholder_text="Ignore words...", fg_color=COLORS["bg_window"], border_width=1, border_color=COLORS["border"], text_color=COLORS["text_main"], height=40)
        self.entry_ignore.pack(fill="x", padx=20, pady=5)

        self.pbar_global = ctk.CTkProgressBar(self.sidebar, height=4, progress_color=COLORS["success"], fg_color=COLORS["border"], width=0)
        self.pbar_global.pack(side="bottom", fill="x")
        self.pbar_global.set(0.0)

        self.btn_start = ctk.CTkButton(self.sidebar, text="START QUEUE  ▶", fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], height=50, corner_radius=25, font=("Segoe UI", 13, "bold"), text_color="white", command=self.start_batch)
        self.btn_start.pack(side="bottom", fill="x", padx=25, pady=30)

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(2, weight=1)

        self.header = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(self.header, text="Dashboard", font=FONTS["display"], text_color=COLORS["text_main"]).pack(side="left")
        self.btn_import = ctk.CTkButton(self.header, text="+ Import", command=self.add_files, fg_color=COLORS["bg_window"], text_color=COLORS["text_main"], hover_color=COLORS["border"], width=100, height=35, corner_radius=20, font=FONTS["body"])
        self.btn_import.pack(side="right")
        self.btn_clear = ctk.CTkButton(self.header, text="Clear", command=self.clear_queue, fg_color="transparent", text_color=COLORS["text_sub"], hover_color=COLORS["bg_window"], width=60, height=35, corner_radius=20, font=FONTS["body"])
        self.btn_clear.pack(side="right", padx=10)

        self.stats_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 30))
        self.stats_frame.grid_columnconfigure((0,1,2), weight=1, uniform="group1")
        self.stat_total = StatWidget(self.stats_frame, "Total Projects", "0", "📁")
        self.stat_total.grid(row=0, column=0, sticky="ew", padx=(0, 15))
        self.stat_done = StatWidget(self.stats_frame, "Completed", "0", "✅")
        self.stat_done.grid(row=0, column=1, sticky="ew", padx=(0, 15))
        self.stat_status = StatWidget(self.stats_frame, "System Status", "Idle", "⚡")
        self.stat_status.grid(row=0, column=2, sticky="ew")

        ctk.CTkLabel(self.main_area, text="Recent Activity", font=FONTS["h2"], text_color=COLORS["text_main"]).grid(row=2, column=0, sticky="nw", pady=(10, 10))
        self.queue_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent", scrollbar_button_color=COLORS["border"])
        self.queue_scroll.grid(row=3, column=0, sticky="nsew")
        self.lbl_empty = ctk.CTkLabel(self.queue_scroll, text="No videos in queue.", font=FONTS["h1"], text_color=COLORS["border"])
        self.lbl_empty.pack(pady=80)

    def safe_get_setting(self, attr_name, default=False):
        full_attr = f"chk_{attr_name}"
        try:
            if hasattr(self, full_attr): return bool(getattr(self, full_attr).get())
            else: return default
        except: return default

    def add_group_header(self, text):
        ctk.CTkLabel(self.settings_frame, text=text, font=FONTS["badge"], text_color=COLORS["text_sub"]).pack(padx=20, pady=(25, 5), anchor="w")

    def add_switch(self, text, default, parent, attr_name):
        saved_val = self.settings_manager.get(attr_name)
        if saved_val is None: saved_val = default
        sw = ModernSwitch(parent, text, default=saved_val, command=lambda: self.save_switch_state(attr_name))
        sw.pack(pady=6, padx=20, anchor="w")
        setattr(self, f"chk_{attr_name}", sw)

    def save_switch_state(self, attr_name):
        self.settings_manager.set(attr_name, bool(getattr(self, f"chk_{attr_name}").get()))

    def save_language_pref(self, choice):
        self.settings_manager.set("language", choice)

    def toggle_theme(self):
        if self.theme_switch.get(): ctk.set_appearance_mode("Dark"); self.settings_manager.set("theme", "Dark"); self.theme_switch.configure(text="Dark Theme")
        else: ctk.set_appearance_mode("Light"); self.settings_manager.set("theme", "Light"); self.theme_switch.configure(text="Light Theme")

    def add_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Videos", "*.mp4 *.mkv *.mov *.avi")])
        if paths:
            try: self.lbl_empty.destroy() 
            except: pass
        for path in paths:
            if path not in self.queue_files:
                self.queue_files.append(path)
                card = JobCard(self.queue_scroll, len(self.queue_files)-1, path)
                card.pack(fill="x", pady=8) 
                self.queue_widgets.append(card)
        self.update_stats()

    def clear_queue(self):
        if self.is_processing: return
        self.queue_files = []
        for w in self.queue_widgets: w.destroy()
        self.queue_widgets = []
        self.update_stats()

    def update_stats(self):
        total = len(self.queue_files)
        done = sum(1 for w in self.queue_widgets if w.lbl_status.cget("text") == "DONE")
        self.stat_total.set_value(total)
        self.stat_done.set_value(done)

    def start_batch(self):
        if not self.queue_files or self.is_processing: return
        self.is_processing = True
        self.stop_requested = False
        self.btn_start.configure(text="PROCESSING...", state="disabled", fg_color=COLORS["bg_sidebar"])
        self.stat_status.set_value("Working")
        threading.Thread(target=self.run_pipeline_loop, daemon=True).start()

    def run_pipeline_loop(self):
        try:
            import torch
            from app import transcriber, translation, dubbing, censor, visual_censor, subtitler
        except Exception as e:
            print(f"Import Error: {e}")
            self.stat_status.set_value("Error")
            return

        output_folder = os.path.abspath("outputs")
        os.makedirs(output_folder, exist_ok=True)

        use_dub = self.safe_get_setting("dub")
        use_burn = self.safe_get_setting("sub")
        use_censor_audio = self.safe_get_setting("censor")
        use_censor_visual = self.safe_get_setting("visual")
        use_docu = self.safe_get_setting("docu")
        use_lipsync = self.safe_get_setting("lipsync")
        need_transcribe = use_dub or use_burn

        if need_transcribe and not self.ai_whisper:
            self.ai_whisper = transcriber.load_model()

        total = len(self.queue_files)
        for i, original_video_path in enumerate(self.queue_files):
            if self.stop_requested: break
            card = self.queue_widgets[i]
            if card.lbl_status.cget("text") == "DONE": continue 
            
            try:
                self.pbar_global.set(i / total)
                self.stat_status.set_value(f"Item {i+1}/{total}")
                original_video_path = os.path.abspath(original_video_path)
                filename = os.path.basename(original_video_path)
                card.set_status("Working...", "blue"); card.set_progress(0.05)
                
                # ----------------------------------------------------
                # AUTO FPS CONVERSION (The PRO FIX)
                # ----------------------------------------------------
                card.set_status("Optimizing FPS", "blue")
                # We convert to 25fps immediately so everything downstream works better
                video_path = convert_to_25fps(original_video_path)
                current_video = video_path
                temp_audio = None 
                
                # 1. Transcribe
                if need_transcribe:
                    card.set_status("Listening", "orange")
                    user_terms = self.entry_ignore.get()
                    segments = transcriber.transcribe_video(self.ai_whisper, video_path, keywords=user_terms)
                    if use_censor_audio:
                        for s in segments:
                            if censor.check_profanity(s['text']): s['text'] += " [BEEP]"
                card.set_progress(0.25)

                # 2. Visual Censor
                if use_censor_visual:
                    card.set_status("Scanning", "orange")
                    timestamps = visual_censor.scan_video_for_content(video_path)
                    if timestamps:
                        safe_path = os.path.join(output_folder, f"Safe_{filename}")
                        visual_censor.apply_blur_to_video(video_path, safe_path, timestamps)
                        if os.path.exists(safe_path) and os.path.getsize(safe_path) > 1024:
                            current_video = safe_path
                card.set_progress(0.50)

                # 3. Translate
                mode = self.combo_lang.get().lower()
                if need_transcribe and "original" not in mode and segments:
                    card.set_status("Translating", "orange")
                    combined_terms = translation.DEFAULT_TECH_TERMS.copy()
                    if self.entry_ignore.get(): combined_terms.extend([x.strip() for x in self.entry_ignore.get().split(",")])
                    segments = translation.translate_segments(segments, target_mode=mode, tech_terms=combined_terms)
                    for seg in segments: seg['text'] = clean_repetitive_text(seg['text'])

                # 4. Dub Generation
                if use_dub and segments:
                    card.set_status("Dubbing", "blue")
                    temp_audio_path = os.path.join(output_folder, "temp_batch_audio.wav")
                    if not self.ai_tts:
                        from TTS.api import TTS
                        device = "cuda" if torch.cuda.is_available() else "cpu"
                        self.ai_tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
                    dubbing.generate_dub_audio(segments, temp_audio_path, current_video, self.ai_tts, mode=mode)
                    if os.path.exists(temp_audio_path): temp_audio = temp_audio_path
                card.set_progress(0.70)

                # ==========================================================
                # 5. NEW: MUSETALK ENGINE CALL (With Shift + FPS Fix)
                # ==========================================================
                if use_lipsync and temp_audio and os.path.exists(temp_audio):
                    card.set_status("Lip Syncing", "purple")
                    
                    # Call the bridge with our new Hindi Optimization (Shift +5)
                    result = call_musetalk_engine(current_video, temp_audio, bbox_shift=5)
                    
                    if result["success"]:
                        print("---------------- ENGINE LOGS START ----------------")
                        print(result["logs"])
                        print("---------------- ENGINE LOGS END ------------------")

                        results_dir = os.path.join(ENGINE_ROOT, "results")
                    
                        # Search for the file
                        found_files = []
                        if os.path.exists(results_dir):
                            for root, dirs, files in os.walk(results_dir):
                                for file in files:
                                    if file.endswith(".mp4"):
                                        found_files.append(os.path.join(root, file))
                    
                        if found_files:
                            current_video = max(found_files, key=os.path.getctime)
                            print(f"[ReFlow] Success! Found: {current_video}")
                        else:
                            print(f"[ReFlow] Engine finished, but folder {results_dir} is empty.")
                
                card.set_progress(0.85)
                # ==========================================================

                # 6. Final FFmpeg Merge
                card.set_status("Merging", "blue")
                final_path = os.path.join(output_folder, f"Processed_{filename}")
                filter_complex = ""; map_audio = "-map 0:a"; inputs = f'-i "{current_video}"'
                
                if temp_audio:
                    inputs += f' -i "{temp_audio}"'
                    if use_docu:
                        filter_complex = '[0:a]volume=0.2[original];[1:a]volume=1.8[dub];[original][dub]amix=inputs=2:duration=first:dropout_transition=2[a_out]'
                        map_audio = '-map "[a_out]"'
                    else: map_audio = '-map 1:a'

                srt_path = ""; map_subs = ""; codec_subs = ""
                if use_burn and segments:
                    srt_path = os.path.join(output_folder, "temp.srt")
                    subtitler.generate_srt(segments, srt_path)
                    inputs += f' -i "{srt_path}"'
                    srt_index = 2 if temp_audio else 1
                    map_subs = f'-map {srt_index}:s'
                    codec_subs = f'-c:s mov_text -metadata:s:s:0 language={mode[:3]}'

                cmd = f'ffmpeg -y -v error {inputs} '
                if filter_complex: cmd += f'-filter_complex "{filter_complex}" '
                cmd += f'-map 0:v {map_audio} {map_subs} '
                if current_video != video_path: cmd += '-c:v libx264 -preset fast '
                else: cmd += '-c:v copy '
                cmd += f'-c:a aac -b:a 192k {codec_subs} -shortest "{final_path}"'
                subprocess.run(cmd, shell=True)
                
                if temp_audio and os.path.exists(temp_audio): os.remove(temp_audio)
                if srt_path and os.path.exists(srt_path): os.remove(srt_path)
                
                card.set_status("Done", "green"); card.set_progress(1.0); self.update_stats()

            except Exception as e:
                print(f"Error: {e}"); card.set_status("Failed", "red"); card.set_progress(0.0)

        self.is_processing = False; self.pbar_global.set(1.0); self.stat_status.set_value("Idle"); self.btn_start.configure(text="START QUEUE", state="normal", fg_color=COLORS["accent"])

if __name__ == "__main__":
    app = ReFlowStudio()
    app.mainloop()