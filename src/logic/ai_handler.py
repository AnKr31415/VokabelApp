import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Client initialisieren (API Key aus .env oder direkt)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_ai_support(wort, ziel_sprache):
    # Versuche diese exakte ID (das ist oft die stabilste für 3.1 Lite)
    model_id = "gemini-3.1-flash-lite-preview"
    
    prompt = f"""
    Gib mir für das Wort '{wort}' in der Sprache {ziel_sprache} folgendes im JSON-Format zurück:
    - 'sentence': Ein einfacher Beispielsatz.
    - 'mnemonic': Eine kreative Eselsbrücke auf Deutsch.
    
    Format: {{"sentence": "...", "mnemonic": "..."}}
    Antworte NUR mit dem rohen JSON.
    """
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        # Bereinigung des Textes
        raw_text = response.text.strip()
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
        
    except Exception as e:
        print(f"KI-Fehler mit {model_id}: {e}")
        # Kleiner Trick: Wenn 3.1 noch nicht verfügbar ist, 
        # nutzen wir automatisch 2.0 als Backup, damit die App nicht crasht.
        if "404" in str(e):
            try:
                response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                return json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            except: return None
        return None