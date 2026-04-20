import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def calculate_relevance_score(regulatory_update_text: str, profile: dict) -> dict:
    """
    Compares a regulatory update against a company profile to generate 
    a relevance score (0.0 to 1.0) and a rationale.
    """
    
    prompt = f"""
    You are an expert Enterprise Governance, Risk, and Compliance (GRC) analyst.
    Determine how relevant the following regulatory update is to this specific company.

    COMPANY CONTEXT:
    - Industry: {profile.get('industry')}
    - Employee Count: {profile.get('employee_count')}
    - Revenue: {profile.get('annual_revenue')}
    - Operating Regions: {', '.join(profile.get('operating_regions', []))}
    - Tech Stack: {', '.join(profile.get('tech_stack', []))}
    - Data Processed: {', '.join(profile.get('data_processed', []))}

    REGULATORY UPDATE:
    {regulatory_update_text}

    Evaluate jurisdiction, industry scope, and company size thresholds.
    Output a strictly valid JSON object with the following schema:
    {{
        "relevance_score": <float between 0.0 and 1.0, where 1.0 is highly critical and 0.0 is completely irrelevant>,
        "rationale": "<A crisp 1-sentence explanation of exactly why this applies or does not apply based on the company context>"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You output strict JSON for GRC relevance scoring."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1 
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Relevance Engine Error: {str(e)}")
        return {"relevance_score": 0.0, "rationale": "Error calculating relevance."}