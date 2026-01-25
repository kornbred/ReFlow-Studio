import gradio as gr
import os
import sys
import torch
import platform
import psutil
import time

# --- INTERNAL PATH SETUP ---
if getattr(sys, 'frozen', False):
    bundle_dir = os.path.join(sys._MEIPASS, "internal")
    sys.path.append(bundle_dir)
    sys.path.append(os.path.join(bundle_dir, "gradio"))
    sys.path.append(os.path.join(bundle_dir, "torch"))
    sys.path.append(os.path.join(bundle_dir, "transformers"))

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

# Try imports
try:
    from pipeline import ReflowPipeline
    from model_manager import ModelManager 
except ImportError:
    print("Core modules not found. Running in UI-Only mode.")
    class ReflowPipeline: pass
    class ModelManager: pass

# --- EMBEDDED CSS ---
CUSTOM_CSS = """
/* --- FONTS --- */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&family=JetBrains+Mono:wght@400;700;900&display=swap');

/* --- THEME --- */
:root {
    --bg-color: #050505;
    --grid-line: #1a1a1a;
    --neon-accent: #ccff00;
    --text-main: #e5e5e5;
}

body { margin: 0; padding: 0; background-color: var(--bg-color); }

/* LAYOUT CONTAINER */
.gradio-container {
    max-width: none !important; width: 100vw !important; height: 100vh !important;
    padding: 0 !important; margin: 0 !important;
    background-color: var(--bg-color) !important;
    display: flex !important; 
    flex-direction: row !important;
    overflow: hidden !important;
}

/* KILL LOADING BARS (Global Kill Switch) */
.progress-level, .loading, .meta-text, .eta-bar, .progress-parent,
#loading_status, .wrap .status, .loader, div[class*="progress"] {
    display: none !important;
    opacity: 0 !important;
    height: 0 !important;
    width: 0 !important;
    pointer-events: none !important;
}

/* --- 1. SIDEBAR (Fixed Width) --- */
.sidebar-panel {
    width: 450px !important;
    min-width: 450px !important;
    height: 100vh !important;
    background: #080808;
    border-right: 4px solid #1a1a1a;
    flex-shrink: 0; z-index: 50;
    display: flex; flex-direction: column;
    overflow-x: hidden !important;
}
.sidebar-panel:hover { border-right-color: #333; }

.sidebar-header { padding: 30px 30px 10px 30px; flex-shrink: 0; }
.sidebar-content { 
    padding: 0 30px; 
    flex-grow: 1; 
    overflow-y: auto; 
    scrollbar-width: none; 
}
.sidebar-footer { 
    padding: 20px 30px 30px 30px; 
    flex-shrink: 0; 
    background: #080808; 
    border-top: 1px solid #1a1a1a;
}

/* --- 2. RIGHT VISUAL PANEL (Scrollable) --- */
.visual-panel {
    flex-grow: 1; 
    height: 100% !important; 
    min-width: 0 !important;
    
    background-color: #050505;
    background-image: 
        linear-gradient(var(--grid-line) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
    background-size: 50px 50px; background-position: center top;
    padding: 30px !important;
    display: flex; flex-direction: column; 
    overflow-y: auto !important; /* Enable Vertical Scroll */
}

/* --- HUD BAR --- */
.hud-bar {
    display: flex !important;
    flex-direction: row !important;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    border: 1px solid #333;
    background: rgba(0,0,0,0.5);
    padding: 15px 25px;
    margin-bottom: 25px;
    font-family: 'JetBrains Mono'; font-size: 0.9rem; color: #888; 
    text-transform: uppercase; letter-spacing: 1px;
}
.hud-value { color: var(--neon-accent); margin-left: 8px; font-weight: 800; }

/* --- PIE CHART SECTION --- */
.bottom-row {
    display: flex; 
    flex-direction: row; 
    flex-wrap: wrap;     
    align-items: flex-start; 
    gap: 30px; 
    margin-top: 20px;
    padding-bottom: 50px; 
}
.pie-wrapper {
    flex-shrink: 0; display: flex; justify-content: center; align-items: center;
}
.pie-chart {
    width: 140px; height: 140px;
    border-radius: 50%;
    background: conic-gradient(var(--neon-accent) var(--degrees, 0deg), #1a1a1a 0deg);
    position: relative;
    display: flex; justify-content: center; align-items: center;
    box-shadow: 0 0 20px rgba(204, 255, 0, 0.1);
}
.pie-chart::before {
    content: ''; position: absolute; width: 100px; height: 100px;
    border-radius: 50%; background: #050505;
}
.pie-text {
    position: relative; z-index: 10; font-family: 'JetBrains Mono';
    font-size: 1.5rem; font-weight: 900; color: white;
}

/* --- TERMINAL --- */
.monitor-frame {
    flex-grow: 1;
    border: 1px solid #333; background: rgba(0,0,0,0.6);
    padding: 4px; position: relative; transition: border-color 0.3s;
}
.monitor-frame:hover { border-color: var(--neon-accent); }
/* Brackets */
.monitor-frame::before { content: ''; position: absolute; top: -1px; left: -1px; width: 10px; height: 10px; border-top: 2px solid var(--neon-accent); border-left: 2px solid var(--neon-accent); }
.monitor-frame::after { content: ''; position: absolute; bottom: -1px; right: -1px; width: 10px; height: 10px; border-bottom: 2px solid var(--neon-accent); border-right: 2px solid var(--neon-accent); }

.terminal-box textarea {
    background-color: #000 !important; color: var(--neon-accent) !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.85rem !important;
    border: none !important; padding: 15px !important; resize: none !important;
    height: 130px !important;
}

/* --- UI ELEMENTS --- */
#cast-group { gap: 8px !important; }
#cast-group label { 
    background: #0f0f0f; border: 1px solid #333; color: #888; 
    padding: 12px; font-size: 0.85rem; font-family: 'JetBrains Mono'; transition: all 0.2s ease;
}
#cast-group label.selected { 
    background: var(--neon-accent) !important; color: black !important; font-weight: 900;
    border-color: var(--neon-accent) !important; box-shadow: 0 0 15px var(--neon-accent);
}

#render-btn {
    height: 60px !important; width: 100%;
    background: var(--neon-accent) !important; color: black !important;
    font-family: 'JetBrains Mono'; font-weight: 900; font-size: 1.1rem;
    border: none !important; border-radius: 0 !important;
    clip-path: polygon(5% 0, 100% 0, 100% 100%, 0 100%);
    margin-top: 10px; transition: all 0.2s ease;
}
#render-btn:hover { 
    background: #fff !important; box-shadow: -5px 0 20px var(--neon-accent); transform: translateX(5px);
}

.gradio-container .video-container, .gradio-container .upload-container { 
    background: #0a0a0a !important; border: 1px dashed #333 !important; 
    border-radius: 0 !important; transition: 0.3s ease;
}
.gradio-container .video-container:hover, .gradio-container .upload-container:hover {
    border-color: var(--neon-accent) !important; box-shadow: 0 0 10px rgba(204, 255, 0, 0.1);
}

h1 { font-size: 3rem !important; line-height: 0.9 !important; margin: 0 !important; letter-spacing: -3px; font-weight: 900; }
.mono-label {
    font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #666; 
    text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; display: flex; align-items: center; font-weight: 700;
}

input[type=range] { -webkit-appearance: none; background: transparent; margin: 15px 0; width: 95% !important; max-width: 100% !important; display: block; }
input[type=range]::-webkit-slider-runnable-track { width: 100%; height: 4px; background: #222; }
input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 16px; width: 16px; background: var(--neon-accent); margin-top: -6px; border: 2px solid black; cursor: pointer; }
"""

# --- UI HELPERS ---
def get_system_stats():
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0).replace("NVIDIA ", "").replace("GeForce ", "")
        gpu_stat = gpu_name
        gpu_dot_color = "var(--neon-accent)"
    else: 
        gpu_stat = "CPU_ONLY"
        gpu_dot_color = "red"
        
    mem = psutil.virtual_memory()
    mem_used = round(mem.used/1024**3, 1)
    mem_total = round(mem.total/1024**3, 1)
    
    return f"""
    <div class="hud-bar">
        <div style="display:flex; align-items:center;">
            <span style="margin-right:10px;">CPU</span>
            <span class="hud-value">{platform.processor().split()[0]}</span>
            <div style="width:8px; height:8px; background:var(--neon-accent); border-radius:50%; margin-left:10px; box-shadow:0 0 5px var(--neon-accent);"></div>
        </div>
        <div style="display:flex; align-items:center;">
            <span style="margin-right:10px;">GPU</span>
            <span class="hud-value">{gpu_stat}</span>
            <div style="width:8px; height:8px; background:{gpu_dot_color}; border-radius:50%; margin-left:10px; box-shadow:0 0 5px {gpu_dot_color};"></div>
        </div>
        <div style="display:flex; align-items:center;">
            <span style="margin-right:10px;">RAM</span>
            <span class="hud-value">{mem_used} / {mem_total} GB</span>
            <div style="width:8px; height:8px; background:var(--neon-accent); border-radius:50%; margin-left:10px;"></div>
        </div>
    </div>
    """

def get_pie_html(percentage, status_text="IDLE"):
    degrees = int((percentage / 100) * 360)
    # [FIX] Added double braces {{ }} around CSS rules so Python doesn't crash
    return f"""
    <style>
        .pie-container .loading, .pie-container .eta-bar, .pie-container .progress {{ display: none !important; opacity: 0 !important; }}
    </style>
    <div class="pie-container" style="display:flex; flex-direction:column; align-items:center; gap:10px; overflow:hidden;">
        <div class="pie-chart" style="--degrees: {degrees}deg;">
            <div class="pie-text">{int(percentage)}%</div>
        </div>
        <div style="font-family:'JetBrains Mono'; color:#666; font-size:0.8rem; letter-spacing:1px; margin-top:10px;">{status_text}</div>
    </div>
    """

# --- WORKER FUNCTIONS ---
def run_script_extraction(video, keep_bg_bool):
    if not video: return None, "> ERROR: NO VIDEO"
    try:
        pipeline = ReflowPipeline()
        data = pipeline.extract_transcript(video, keep_background=keep_bg_bool)
        log = f"> SCRIPT EXTRACTED.\n> FOUND {len(data)} LINES."
        return data, log
    except Exception as e:
        return None, f"> ERROR: {str(e)}"

def run_render(video, cast_selection, blur_level, pitch_adj, target_lang, user_voice_file, lip_sync_bool, enhance_bool, keep_bg_bool, manual_script_data):
    if not video: 
        yield None, "> ERROR: NO SOURCE VIDEO SELECTED", get_pie_html(0, "ERROR")
        return
    
    log = f"> INITIALIZING v0.5 PIPELINE...\n"
    log += f"> TARGET LANGUAGE: {target_lang}\n"
    yield None, log, get_pie_html(5, "INIT")
    
    try:
        pipeline = ReflowPipeline()
    except Exception as e:
        log += f"> CRITICAL ERROR STARTING PIPELINE: {e}\n"
        yield None, log, get_pie_html(0, "FAIL")
        return

    script_to_use = None
    if manual_script_data is not None and len(manual_script_data) > 0:
        try:
            if str(manual_script_data[0][2]).strip():
                script_to_use = manual_script_data
        except: pass

    try:
        for progress_val, status_text, result_path in pipeline.process_video_gen(
            video_path=video, cast_list=cast_selection, blur_strength=blur_level, 
            pitch_shift=pitch_adj, target_lang=target_lang, user_voice_path=user_voice_file,
            lip_sync_active=lip_sync_bool, enhance_active=enhance_bool, 
            keep_background=keep_bg_bool, manual_script=script_to_use
        ):
            if result_path is None:
                if "SEG" not in status_text: log += f"> PHASE: {status_text}...\n"
                yield None, log, get_pie_html(progress_val, status_text)
            else:
                log += "\n" + "="*30 + "\n"
                log += "> RENDER COMPLETE SUCCESSFULLY! ✅\n"
                log += f"> FILE: {os.path.basename(result_path)}"
                abs_path = os.path.abspath(result_path)
                yield gr.update(value=abs_path), log, get_pie_html(100, "DONE")
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        log += f"\n> FATAL PIPELINE CRASH:\n{error_trace}"
        print(error_trace)
        yield None, log, get_pie_html(0, "CRASHED")

def run_install(url):
    if not url: return "❌ Error: No URL provided", gr.update()
    yield "> DOWNLOAD_STARTED...", gr.update()
    try:
        manager = ModelManager()
        result = manager.install_model(url)
        new_voices = get_voices()
        yield f"> {result}", gr.CheckboxGroup.update(choices=new_voices, value=["CLONED_USER"])
    except:
        yield "> INSTALL FAILED", gr.update()

def get_voices():
    weights_dir = os.path.join(os.getcwd(), "models", "rvc", "weights")
    if not os.path.exists(weights_dir): return ["CLONED_USER"]
    models = [f.replace(".pth", "") for f in os.listdir(weights_dir) if f.endswith(".pth")]
    models.insert(0, "CLONED_USER")
    return models

def update_blur_text(val):
    if val <= 15: return "🧸 **FAMILY** — Heavy Censor"
    elif val <= 35: return "📺 **SAFE** — TV Friendly"
    elif val <= 60: return "🎬 **CINEMA** — Balanced"
    elif val <= 85: return "🔥 **RAW** — Minimal Filters"
    else: return "💀 **UNCUT** — No Mercy"


# --- GRADIO INTERFACE ---
with gr.Blocks(css=CUSTOM_CSS, title="Reflow Studio v0.5") as demo:
    pitch_state = gr.State(value=0)

    # LAYOUT ROW (Sidebar + Main)
    with gr.Row(elem_classes="gradio-container"):
        
        # --- LEFT SIDEBAR (Width fixed to 450px in CSS) ---
        with gr.Column(elem_classes="sidebar-panel"):
            with gr.Column(elem_classes="sidebar-header"):
                gr.HTML("""
                <div style="display:flex; justify-content:space-between; border-bottom:1px solid #333; padding-bottom:10px; margin-bottom:10px;">
                    <span style="font-family:'JetBrains Mono'; font-size:0.7rem; color:#666;">SYSTEM v0.5</span>
                    <span style="color:#ccff00; font-family:'JetBrains Mono'; font-size:0.7rem; animation: blink 2s infinite;">ONLINE ●</span>
                </div>
                <div>
                    <h1 style="font-size:3rem; line-height:0.9; margin:0; letter-spacing:-2px; color:white;">REFLOW</h1>
                    <h1 style="font-size:3rem; line-height:0.9; margin:0; letter-spacing:-2px; color:#ccff00;">STUDIO</h1>
                </div>
                """)

            with gr.Column(elem_classes="sidebar-content"):
                with gr.Tabs():
                    with gr.TabItem("MAIN"):
                        gr.HTML("""<div style="font-family:'JetBrains Mono'; font-size:0.75rem; color:#666; margin-top:20px;">01 // VOICE CAST</div>""")
                        cast_selector = gr.CheckboxGroup(choices=get_voices(), value=["CLONED_USER"], label=None, elem_id="cast-group")

                        gr.HTML('<br><div style="font-family:JetBrains Mono; font-size:0.75rem; color:#666;">02 // LANGUAGE</div>')
                        lang_dropdown = gr.Dropdown(choices=[("English", "en"), ("Hindi", "hi"), ("Japanese", "ja"), ("Korean", "ko")], value="en", label=None, container=False)
                        
                        gr.HTML('<br><div style="font-family:JetBrains Mono; font-size:0.75rem; color:#666;">03 // MIXER & VIDEO</div>')
                        keep_bg_chk = gr.Checkbox(label="PRESERVE MUSIC/SFX", value=True)
                        lip_sync_chk = gr.Checkbox(label="ENABLE WAV2LIP", value=False)
                        enhance_chk = gr.Checkbox(label="ENHANCE FACE (High-Def)", value=False)
                        
                        # --- VISION METER IN SIDEBAR ---
                        gr.HTML('<br><div style="font-family:JetBrains Mono; font-size:0.75rem; color:#666;">04 // VISION METER</div>')
                        blur_slider = gr.Slider(1, 101, 15, step=2, label=None, container=False)
                        blur_status = gr.Markdown("🧸 **FAMILY MODE**")

                    with gr.TabItem("SCRIPT 📝"):
                        gr.Markdown("*Edit text below to override AI.*")
                        script_table = gr.Dataframe(headers=["Start", "End", "Text"], datatype=["number", "number", "str"], col_count=(3, "fixed"), interactive=True, type="array")
                        analyze_btn = gr.Button("🔍 ANALYZE SCRIPT", size="sm", variant="secondary")

                    with gr.TabItem("VOICE LAB"):
                        gr.HTML('<br><div class="mono-label">UPLOAD REFERENCE</div>')
                        user_voice_input = gr.Audio(type="filepath", label=None)

                    with gr.TabItem("MODELS"):
                        model_url_input = gr.Textbox(placeholder="Model URL", label=None)
                        install_btn = gr.Button("INSTALL MODEL", size="sm")

            with gr.Column(elem_classes="sidebar-footer", visible=False): pass

        # --- RIGHT VISUAL PANEL ---
        with gr.Column(elem_classes="visual-panel"):
            
            # 1. HUD & RENDER BTN
            with gr.Group():
                gr.HTML(get_system_stats()) 
                render_btn = gr.Button("INITIALIZE RENDER >>", elem_id="render-btn")

            # 2. VIDEO GRID
            with gr.Row(elem_classes="io-row"):
                with gr.Column(elem_classes="monitor-frame"):
                    gr.HTML('<div style="color:#ccff00; font-family:JetBrains Mono; font-size:0.7rem; margin-bottom:5px;">// INPUT SOURCE</div>')
                    video_input = gr.Video(label=None, interactive=True)
                
                with gr.Column(elem_classes="monitor-frame"):
                    gr.HTML('<div style="color:#ccff00; font-family:JetBrains Mono; font-size:0.7rem; margin-bottom:5px;">// RENDER OUTPUT</div>')
                    video_output = gr.Video(label=None, interactive=False)
            
            # 3. BOTTOM LOGGING AREA
            with gr.Row(elem_classes="bottom-row"):
                with gr.Column(scale=0, min_width=150):
                    progress_chart = gr.HTML(get_pie_html(0, "IDLE"))
                
                with gr.Column(scale=1):
                    gr.HTML('<div style="font-family:JetBrains Mono; color:#666; font-size:0.7rem; margin-bottom:5px;">// SYSTEM_LOG</div>')
                    status_log = gr.Textbox(value="> STANDBY...", label=None, interactive=False, lines=6, elem_classes="monitor-frame terminal-box")

    blur_slider.change(fn=update_blur_text, inputs=blur_slider, outputs=blur_status)
    analyze_btn.click(run_script_extraction, inputs=[video_input, keep_bg_chk], outputs=[script_table, status_log])
    render_btn.click(run_render, inputs=[video_input, cast_selector, blur_slider, pitch_state, lang_dropdown, user_voice_input, lip_sync_chk, enhance_chk, keep_bg_chk, script_table], outputs=[video_output, status_log, progress_chart])
    install_btn.click(run_install, inputs=[model_url_input], outputs=[status_log, cast_selector])

if __name__ == "__main__":
    demo.queue().launch(inbrowser=True, share=False)