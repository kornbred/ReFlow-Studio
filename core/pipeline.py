import os
import sys
import subprocess
import gc
import json
import logging
import shutil
import datetime
from pydub import AudioSegment, effects
# Ensure these imports exist in your project structure
from audio_separator import AudioSeparator
from llm_translator import LLMTranslator
from enhancer import FaceEnhancer

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class ReflowPipeline:
    def __init__(self):
        # Adjust this path if your project folder is different
        self.root_dir = r"D:\New folder\Reflow-Studio"
        self.temp_dir = os.path.join(self.root_dir, "temp")
        self.output_dir = os.path.join(self.root_dir, "outputs")
        self.stt_worker_script = os.path.join(self.root_dir, "core", "run_stt.py")
        
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def clear_vram(self):
        gc.collect()
        try:
            import torch
            torch.cuda.empty_cache()
        except: pass

    def format_timestamp(self, seconds):
        td = datetime.timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        millis = int((seconds - total_seconds) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    def generate_srt(self, transcript, output_path):
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, seg in enumerate(transcript):
                    start = self.format_timestamp(seg['start'])
                    end = self.format_timestamp(seg['end'])
                    text = seg['text'].strip()
                    if not text: continue
                    f.write(f"{i+1}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{text}\n\n")
        except Exception as e:
            print(f"⚠️ Error generating SRT: {e}")

    def get_duration(self, file_path):
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        try: return float(subprocess.check_output(cmd).decode().strip())
        except: return 0.0

    def speed_change(self, sound, speed=1.0):
        if speed == 1.0: return sound
        temp_in = os.path.join(self.temp_dir, "stretch_in.wav")
        temp_out = os.path.join(self.temp_dir, "stretch_out.wav")
        sound.export(temp_in, format="wav")
        cmd = ['ffmpeg', '-y', '-i', temp_in, '-filter:a', f"atempo={speed}", '-vn', temp_out]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if os.path.exists(temp_out): return AudioSegment.from_file(temp_out)
        return sound

    def merge_av(self, video_path, audio_path, srt_path, output_path):
        import subprocess
        import os

        # Defines temporary output name
        clean_output = output_path.replace(".mp4", "_CLEAN.mp4")
        
        # Build the FFmpeg command
        # This takes video + audio + subtitles and merges them into one file
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",          # Copy video stream (fast, no re-encode)
            "-c:a", "aac",           # Encode audio to AAC
            "-strict", "experimental",
            clean_output
        ]

        print(f"> MERGING A/V: {video_path} + {audio_path} -> {clean_output}")

        try:
            # Run FFmpeg and capture the output to see errors
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print("\n❌ FFmpeg Merge Failed!")
            print("Error Log:", e.stderr)
            return None
        except FileNotFoundError:
            print("\n❌ FFmpeg not found! Please ensure FFmpeg is installed and added to PATH.")
            return None

        # Only rename if the file actually exists
        if os.path.exists(clean_output):
            if os.path.exists(output_path):
                os.remove(output_path) # Delete old file if exists
            os.rename(clean_output, output_path)
            return output_path
        else:
            print(f"\n❌ Error: Output file {clean_output} was not created by FFmpeg.")
            return None

    # --- MAIN PROCESSOR (GENERATOR MODE) ---
    def process_video_gen(self, video_path, cast_list, blur_strength=15, pitch_shift=0, target_lang="en", user_voice_path=None, lip_sync_active=False, enhance_active=False, keep_background=True, manual_script=None):
        """
        Yields tuple: (progress_percent, log_message, result_path)
        result_path is None until the very last yield.
        """
        print(f"[DEBUG] Pipeline Generator v0.5 Started.")
        if not os.path.exists(video_path): 
            yield (0, "ERROR: NO VIDEO FILE", None)
            return

        if not cast_list: cast_list = ["CLONED_USER"]
        
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        final_output = os.path.join(self.output_dir, f"{base_name}_DUBBED_{target_lang.upper()}.mp4")
        
        temp_video_out = os.path.join(self.temp_dir, "temp_visuals.mp4")
        temp_audio_in = os.path.join(self.temp_dir, "original_audio.wav")
        temp_srt = os.path.join(self.temp_dir, "temp_subs.srt")
        transcript_json = os.path.join(self.temp_dir, "transcript.json")
        master_audio_path = os.path.join(self.temp_dir, "master_audio.wav")
        
        # Initial extraction
        subprocess.run(['ffmpeg', '-y', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', temp_audio_in], stdout=subprocess.DEVNULL)
        total_duration = self.get_duration(video_path)

        # STAGE 0: SEPARATION
        yield (10, "SEPARATING AUDIO", None)
        bg_track = None
        if keep_background:
            separator = AudioSeparator()
            vocals_path, bg_path = separator.separate(temp_audio_in)
            if bg_path:
                bg_track = AudioSegment.from_file(bg_path)
                bg_track = bg_track - 2 
        else:
            vocals_path = temp_audio_in

        # STAGE 1: INTELLIGENT SCRIPTING
        yield (20, "TRANSCRIBING", None)
        transcript = []
        
        if manual_script is not None and len(manual_script) > 0:
            for row in manual_script:
                if str(row[2]).strip():
                    transcript.append({
                        'start': float(row[0]),
                        'end': float(row[1]),
                        'text': str(row[2])
                    })
        else:
            transcription_source = vocals_path if (keep_background and vocals_path) else temp_audio_in
            subprocess.run([sys.executable, self.stt_worker_script, transcription_source, transcript_json], check=True)
            with open(transcript_json, 'r', encoding='utf-8') as f: 
                transcript = json.load(f)

        # STAGE 2: TRANSLATION
        if manual_script is None and target_lang != "source":
            yield (35, "AI TRANSLATING", None)
            lang_map = {"en": "English", "hi": "Hindi", "ja": "Japanese", "ko": "Korean", "es": "Spanish", "fr": "French"}
            target_name = lang_map.get(target_lang, "English")
            
            brain = LLMTranslator()
            for i, seg in enumerate(transcript):
                original = seg['text']
                translated = brain.translate(original, target_name)
                seg['text'] = translated

        self.generate_srt(transcript, temp_srt)

        # STAGE 3: VISION PREP
        subprocess.run(['ffmpeg', '-y', '-i', video_path, '-c:v', 'copy', '-an', temp_video_out], stdout=subprocess.DEVNULL)

        # STAGE 4: DUBBING
        yield (45, "INITIALIZING TTS", None)
        from tts.tts_handler import TTSHandler
        from rvc.rvc_handler import RVCHandler
        
        tts = TTSHandler()
        rvc = RVCHandler(device="cuda")
        
        if bg_track: master_track = bg_track
        else: master_track = AudioSegment.silent(duration=int(total_duration * 1000))
        
        total_segments = len(transcript)
        for i, segment in enumerate(transcript):
            # Calculate micro-progress for smooth UI updates
            # Dubbing goes from 45% to 75%
            current_progress = 45 + int((i / total_segments) * 30)
            yield (current_progress, f"DUBBING SEG {i+1}/{total_segments}", None)

            text = segment['text'].strip()
            if not text: continue
            
            actor = cast_list[i % len(cast_list)]
            
            seg_xtts = os.path.join(self.temp_dir, f"seg_{i}_xtts.wav")
            seg_final = os.path.join(self.temp_dir, f"seg_{i}_final.wav")

            if actor == "CLONED_USER" and user_voice_path:
                tts.generate_audio(text, seg_xtts, language=target_lang, ref_wav=user_voice_path)
            else:
                tts.generate_audio(text, seg_xtts, language=target_lang)
            
            if actor != "CLONED_USER":
                raw = AudioSegment.from_file(seg_xtts)
                effects.normalize(raw, headroom=3.0).export(seg_xtts, format="wav")
                rvc.infer(seg_xtts, seg_final, model_name=actor)
            else:
                shutil.copy(seg_xtts, seg_final)

            clip = AudioSegment.from_file(seg_final)
            target_dur = (segment['end'] - segment['start']) * 1000
            
            if len(clip) > 0 and target_dur > 500:
                speed = len(clip) / target_dur
                speed = max(0.7, min(speed, 1.5))
                clip = self.speed_change(clip, speed)
                clip = clip + 2
                master_track = master_track.overlay(clip, position=int(segment['start']*1000))
            
            if os.path.exists(seg_xtts): os.remove(seg_xtts)
            if os.path.exists(seg_final): os.remove(seg_final)

        master_track.export(master_audio_path, format="wav")
        del tts, rvc
        self.clear_vram()

        # STAGE 5: LIP SYNC
        video_to_merge = temp_video_out
        if lip_sync_active:
            yield (80, "LIP SYNCING", None)
            from lipsync_handler import LipSyncHandler
            syncer = LipSyncHandler()
            result_video = syncer.execute(temp_video_out, master_audio_path, os.path.join(self.temp_dir, "temp_visuals_lipsync.mp4"))
            if result_video: video_to_merge = result_video
            
            # STAGE 6: ENHANCEMENT
            if enhance_active:
                yield (90, "ENHANCING FACE", None)
                from enhancer import FaceEnhancer
                enhancer = FaceEnhancer()
                result_enhanced = enhancer.enhance(video_to_merge, os.path.join(self.temp_dir, "temp_visuals_enhanced.mp4"))
                if result_enhanced: video_to_merge = result_enhanced

        # STAGE 7: MERGE
        yield (95, "FINAL MERGE", None)
        self.merge_av(video_to_merge, master_audio_path, temp_srt, final_output)
        
        # COMPLETE
        yield (100, "COMPLETE", final_output)