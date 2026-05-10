import os
import json
from openai import OpenAI
from typing import Any, Dict, List, Optional

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_risk_suggestions(
    profile_dict: Dict[str, Any], 
    active_matrix: Optional[Dict[str, Any]], 
    existing_risks: List[str]
) -> Dict[str, Any]:
    """
    Generates tailored AI risk suggestions based on company profile 
    and existing risks to avoid duplicates.
    """
    
    # Safely determine matrix scales for the prompt
    prob_list = active_matrix.get('probability', []) if active_matrix else []
    imp_list = active_matrix.get('impact', []) if active_matrix else []
    
    max_likelihood = max([p.get('level', 4) for p in prob_list]) if prob_list else 4
    max_impact = max([i.get('level', 4) for i in imp_list]) if imp_list else 4

    system_prompt = f"""
    You are an expert Chief Information Security Officer (CISO).
    Analyze the provided company profile and generate highly specific, realistic cybersecurity and compliance risks tailored to their industry, tech stack, and data processed.
    
    CRITICAL RULES:
    1. Do NOT suggest any risks that are similar or identical to these already existing risks: {json.dumps(existing_risks)}
    2. Generate up to 5 NEW risks. If you cannot think of new risks that do not overlap, return an empty list.
    
    The risk likelihood scale goes from 1 to {max_likelihood}.
    The risk impact scale goes from 1 to {max_impact}.
    
    Output strictly in this JSON schema:
    {{
        "suggestions": [
            {{
                "name": "string (Specific risk scenario)",
                "category": "string (Cybersecurity, Privacy, Vendor Risk, Infrastructure)",
                "likelihood": integer,
                "impact": integer,
                "owner": "string (Suggested job title to own this risk)"
            }}
        ]
    }}
    """
    
    user_prompt = f"COMPANY PROFILE:\n{json.dumps(profile_dict, indent=2)}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        if not content:
            return {"suggestions": []}
            
        return json.loads(content)
        
    except Exception as e:
        print(f"Risk Engine AI Error: {str(e)}")
        return {"suggestions": []}