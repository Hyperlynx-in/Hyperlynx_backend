import os
from openai import OpenAI
import json
from typing import Any, Dict, List, Optional

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_framework_suggestions(
    profile_dict: Dict[str, Any], 
    available_frameworks: List[Dict[str, Any]], 
    current_frameworks: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Analyzes company profile against available frameworks to suggest Add/Keep/Remove actions.
    """
    if current_frameworks is None:
        current_frameworks = []
        
    system_prompt = """
    You are an expert Governance, Risk, and Compliance (GRC) consultant.
    Analyze the company's profile and determine exactly which frameworks apply to them.
    
    If the user already has saved frameworks (CURRENTLY SAVED FRAMEWORKS), evaluate them against the NEW profile:
    - If it still applies, mark action as "Keep".
    - If a new framework applies, mark action as "Add".
    - If a previously saved framework NO LONGER applies (e.g., they removed Healthcare from their profile so HIPAA is invalid), mark action as "Remove".
    
    Output strictly in this JSON schema:
    {
        "suggestions": [
            {
                "framework_id": "string (must exactly match the provided id)",
                "name": "string",
                "category": "string",
                "confidence": integer (0 to 100),
                "reason": "string",
                "is_mandatory": boolean,
                "action": "Keep" | "Add" | "Remove"
            }
        ]
    }
    """
    
    user_prompt = f"""
    COMPANY PROFILE:
    {json.dumps(profile_dict, indent=2)}
    
    CURRENTLY SAVED FRAMEWORKS (Evaluate these!):
    {json.dumps(current_frameworks, indent=2)}
    
    AVAILABLE MASTER CATALOG:
    {json.dumps(available_frameworks, indent=2)}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        if not content:
            return {"suggestions": []}
            
        return json.loads(content)
        
    except Exception as e:
        print(f"Applicability Engine Error: {str(e)}")
        return {"suggestions": []}