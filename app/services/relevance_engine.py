# app/services/relevance_engine.py
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def calculate_relevance_score(regulatory_update_text: str, profile: dict) -> dict:
    """
    Compares a regulatory update against a company profile to generate 
    a relevance score (0.0 to 1.0) and a rationale.
    """
    
    # Safely extract all fields, defaulting to 'None specified' if empty
    industry = profile.get('industry', 'Unknown')
    employee_count = profile.get('employee_count', 'Unknown')
    revenue = profile.get('annual_revenue', 'Unknown')
    regions = ', '.join(profile.get('operating_regions') or ['None specified'])
    services = ', '.join(profile.get('services_provided') or ['None specified'])
    authorities = ', '.join(profile.get('regulatory_authorities') or ['None specified'])
    tech_stack = ', '.join(profile.get('tech_stack') or ['None specified'])
    data_processed = ', '.join(profile.get('data_processed') or ['None specified'])

    prompt = f"""
    You are an expert Enterprise Governance, Risk, and Compliance (GRC) analyst.
    Determine how relevant the following regulatory update is to this specific organization.

    ORGANISATION CONTEXT PROFILE:
    - Sector/Industry: {industry}
    - Services Provided: {services}
    - Size (Employees / Revenue): {employee_count} / {revenue}
    - Operating Regions: {regions}
    - Governing Authorities: {authorities}
    - Tech Stack & Infrastructure: {tech_stack}
    - Data Types Processed: {data_processed}

    REGULATORY UPDATE TO EVALUATE:
    \"\"\"{regulatory_update_text}\"\"\"

    EVALUATION CRITERIA:
    1. Jurisdiction Match: Does the update apply to their Operating Regions?
    2. Authority Match: Is the update issued by one of their Governing Authorities?
    3. Service/Sector Match: Does it target their specific Services Provided or Sector?
    4. Data/Tech Match: Does it regulate the Data Types they process or their Tech Stack?
    5. Size Thresholds: Do they meet the employee/revenue thresholds mentioned in the update (if any)?

    Output a strictly valid JSON object with the following schema:
    {{
        "relevance_score": <float between 0.0 and 1.0, where 1.0 is highly critical/direct match and 0.0 is completely irrelevant>,
        "rationale": "<A crisp 1-sentence explanation of exactly why this applies or does not apply based strictly on the organisation's context>"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise GRC applicability engine. Output strict JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1 
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Relevance Engine Error: {str(e)}")
        return {"relevance_score": 0.0, "rationale": "Error calculating relevance."}