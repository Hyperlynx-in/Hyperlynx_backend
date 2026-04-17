import os
import json
from openai import OpenAI

client = OpenAI()

def generate_simple_summary(legal_text):
    """Takes dense regulatory text and returns a 1-2 sentence plain-English summary."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a cybersecurity compliance expert communicating with busy executives. Translate the following regulatory update into a simple, 1 to 2 sentence summary that anyone can understand. Focus on the core 'what' and 'why'. Do not use jargon. Output ONLY the summary."
                },
                {
                    "role": "user", 
                    "content": legal_text
                }
            ],
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        return None

def extract_obligations(legal_text):
    """
    Extracts actionable compliance mandates and returns them as a Python list.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system", 
                    "content": """You are a strict compliance extraction engine. Your job is to extract actionable obligations, mandates, and 'what you must do' requirements from regulatory text. 
                    Return ONLY a JSON object with a single key 'obligations' containing a list of strings. 
                    If there are no clear obligations, return an empty list. 
                    Example output: {"obligations": ["Must report breaches within 72 hours", "Must enforce MFA on admin accounts"]}"""
                },
                {
                    "role": "user", 
                    "content": legal_text
                }
            ],
            temperature=0.1 
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("obligations", [])
        
    except Exception as e:
        print(f"OpenAI Extraction Error: {str(e)}")
        return None