import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_framework_suggestions(profile_dict, available_frameworks):
    system_prompt = """
    You are an expert Governance, Risk, and Compliance (GRC) consultant.
    Analyze the company's profile and determine exactly which cybersecurity and privacy frameworks apply to them from the provided list.
    
    Output strictly in this JSON schema:
    {
        "suggestions": [
            {
                "framework_id": "string (must exactly match the provided id)",
                "name": "string",
                "category": "string (e.g., Privacy, ISMS, Payment, Healthcare)",
                "confidence": integer (0 to 100 representing how strongly this applies based on their context),
                "reason": "string (A 1-sentence clear explanation of WHY this applies)",
                "is_mandatory": boolean (true if legally required, false if recommended best practice)
            }
        ]
    }
    """
    
    user_prompt = f"""
    COMPANY PROFILE:
    {json.dumps(profile_dict, indent=2)}
    
    AVAILABLE FRAMEWORKS TO CHOOSE FROM:
    {json.dumps(available_frameworks, indent=2)}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1
    )
    
    return json.loads(response.choices[0].message.content)