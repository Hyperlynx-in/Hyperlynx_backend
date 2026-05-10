import os
import json
from openai import OpenAI
from typing import Any, Dict, Optional

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_simple_summary(legal_text: str) -> Optional[str]:
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
        
        content = response.choices[0].message.content
        if content:
            return content.strip()
        return None

    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        return None

def extract_obligations(legal_text: str) -> Optional[Dict[str, Any]]:
    """
    Analyzes regulatory text to calculate an impact score, map frameworks, 
    and extract structured compliance obligations.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system", 
                    "content": """You are an elite GRC (Governance, Risk, and Compliance) AI extraction engine. 
                    Analyze the regulatory update and return ONLY a JSON object with this exact schema:
                    {
                      "impact_score": <Integer 1-10 based on urgency, operational scope, and penalty risk>,
                      "frameworks": [<List of strings. Guess the affected frameworks if not explicitly stated, e.g., "NIST CSF", "ISO 27001", "GDPR", "SOC2", "DORA". Limit to top 3.>],
                      "obligations": [
                        {
                          "action": "<Action verb, e.g., Implement, Audit, Report, Patch>",
                          "subject": "<What specifically needs to be done>",
                          "deadline": "<Extract deadline as YYYY-MM-DD, or 'Not Specified'>",
                          "penalty_risk": "<High, Medium, or Low>"
                        }
                      ]
                    }
                    If there are no clear obligations, return an empty list for 'obligations'."""
                },
                {
                    "role": "user", 
                    "content": legal_text
                }
            ],
            temperature=0.1 
        )
        
        content = response.choices[0].message.content
        if not content:
            return None
            
        result: Dict[str, Any] = json.loads(content)
        return result
        
    except Exception as e:
        print(f"OpenAI Extraction Error: {str(e)}")
        return None