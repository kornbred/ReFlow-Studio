import requests
import json
import logging

class LLMTranslator:
    def __init__(self, model="llama3"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"
        print(f"[LLM] 🧠 Initializing Local Intelligence ({self.model})...")
        
        # Check connection
        try:
            response = requests.get("http://localhost:11434/")
            if response.status_code == 200:
                print("[LLM] ✅ Connection Established (Direct Mode).")
            else:
                print("[LLM] ⚠️ Ollama is running but returned unexpected status.")
        except Exception:
            print("[LLM] ⚠️ WARNING: Ollama not reachable. Make sure the app is running!")

    def translate(self, text, target_lang_name):
        """
        Sends text to Llama 3 via raw HTTP request to avoid Pydantic conflicts.
        """
        prompt = (
            f"You are a professional subtitle translator for movies. "
            f"Translate the following text into natural, spoken {target_lang_name}. "
            f"Keep the meaning identical but make it sound like a native speaker. "
            f"Do not add explanations, quotes, or notes. Just the translation.\n\n"
            f"Original: \"{text}\"\n"
            f"Translation:"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            # Direct HTTP POST Request
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            # Parse Response
            data = response.json()
            translated_text = data.get('response', '').strip().replace('"', '')
            return translated_text
            
        except Exception as e:
            print(f"[LLM] ❌ Error: {e}")
            return text # Fallback to original text if AI fails