import json
import requests
from django.conf import settings


def build_message_variables(workspace, lead=None, campaign=None):
    return {
        "company_name": workspace.company_name,
        "company_website": workspace.company_website or "",
        "business_type": workspace.business_type or "",
        "industry": workspace.industry or "",
        "company_size": workspace.company_size or "",
        "sender_name": workspace.sender_name,
        "sender_email": workspace.sender_email,
        "sender_position": workspace.sender_position or "",
        "business_description": workspace.business_description or "",
        "product_service_summary": workspace.product_service_summary or "",
        "target_audience": workspace.target_audience or "",
        "unique_selling_points": workspace.unique_selling_points or "",
        "default_email_tone": workspace.default_email_tone or "professional",

        "lead_first_name": lead.first_name if lead else "",
        "lead_last_name": lead.last_name if lead else "",
        "lead_full_name": lead.full_name if lead else "",
        "lead_email": lead.email if lead else "",
        "lead_phone": lead.phone if lead else "",
        "lead_company_name": lead.company_name if lead else "",
        "lead_company_website": lead.company_website if lead else "",
        "lead_industry": lead.industry if lead else "",
        "lead_job_title": lead.job_title if lead else "",
        "lead_linkedin_url": lead.linkedin_url if lead else "",
        "lead_city": lead.city if lead else "",
        "lead_country": lead.country if lead else "",
        "lead_notes": lead.notes if lead else "",

        "campaign_name": campaign.name if campaign else "",
        "campaign_description": campaign.description if campaign else "",
        "campaign_objective": campaign.objective if campaign else "",
        "campaign_target_audience": campaign.target_audience if campaign else "",
        "campaign_offer_summary": campaign.offer_summary if campaign else "",
    }


def build_prompt(message_type, variables, custom_instruction=""):
    system_prompt = f"""
You are an expert B2B sales outreach copywriter.

Your job is to write concise, personalized cold outreach emails.
Output must be professional, natural, human-like, and specific.
Avoid hype, spammy language, exaggerated claims, and fake personalization.

Rules:
1. Write in plain business English.
2. Keep subject under 10 words if possible.
3. Keep email body concise.
4. Make the message relevant to the lead's role/company if data exists.
5. Mention the sender's company/service naturally.
6. Do not use markdown.
7. Return valid JSON only in this exact format:
{{
  "subject": "...",
  "body": "..."
}}
"""

    message_goal_map = {
        "initial": "Write a first cold outreach email.",
        "follow_up": "Write a follow-up email referencing a previous outreach politely.",
        "custom": "Write a custom outreach email based on the instruction.",
    }

    user_prompt = f"""
Task:
{message_goal_map.get(message_type, "Write a personalized outreach email.")}

Workspace and sender context:
{json.dumps({
    "company_name": variables["company_name"],
    "company_website": variables["company_website"],
    "business_type": variables["business_type"],
    "industry": variables["industry"],
    "sender_name": variables["sender_name"],
    "sender_email": variables["sender_email"],
    "sender_position": variables["sender_position"],
    "business_description": variables["business_description"],
    "product_service_summary": variables["product_service_summary"],
    "target_audience": variables["target_audience"],
    "unique_selling_points": variables["unique_selling_points"],
    "default_email_tone": variables["default_email_tone"],
}, ensure_ascii=False, indent=2)}

Lead context:
{json.dumps({
    "first_name": variables["lead_first_name"],
    "last_name": variables["lead_last_name"],
    "full_name": variables["lead_full_name"],
    "email": variables["lead_email"],
    "company_name": variables["lead_company_name"],
    "company_website": variables["lead_company_website"],
    "industry": variables["lead_industry"],
    "job_title": variables["lead_job_title"],
    "linkedin_url": variables["lead_linkedin_url"],
    "city": variables["lead_city"],
    "country": variables["lead_country"],
    "notes": variables["lead_notes"],
}, ensure_ascii=False, indent=2)}

Campaign context:
{json.dumps({
    "campaign_name": variables["campaign_name"],
    "campaign_description": variables["campaign_description"],
    "campaign_objective": variables["campaign_objective"],
    "campaign_target_audience": variables["campaign_target_audience"],
    "campaign_offer_summary": variables["campaign_offer_summary"],
}, ensure_ascii=False, indent=2)}

Additional instruction:
{custom_instruction or "No additional instruction."}
"""
    return system_prompt.strip(), user_prompt.strip()


def call_openai_chat_completion(api_key, model_name, system_prompt, user_prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name or settings.AI_DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
    }

    response = requests.post(
        settings.AI_OPENAI_API_URL,
        headers=headers,
        json=payload,
        timeout=settings.AI_REQUEST_TIMEOUT,
    )

    response.raise_for_status()
    data = response.json()

    content = data["choices"][0]["message"]["content"]
    return data, content


def parse_ai_json_content(content):
    cleaned = content.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    parsed = json.loads(cleaned)

    return {
        "subject": parsed.get("subject", "").strip(),
        "body": parsed.get("body", "").strip(),
    }


def render_template_variables(text, variables):
    if not text:
        return text

    replacements = {
        "{{first_name}}": variables.get("lead_first_name", ""),
        "{{last_name}}": variables.get("lead_last_name", ""),
        "{{full_name}}": variables.get("lead_full_name", ""),
        "{{company_name}}": variables.get("lead_company_name", ""),
        "{{job_title}}": variables.get("lead_job_title", ""),
        "{{sender_name}}": variables.get("sender_name", ""),
        "{{sender_position}}": variables.get("sender_position", ""),
        "{{sender_company}}": variables.get("company_name", ""),
    }

    for key, value in replacements.items():
        text = text.replace(key, value or "")

    return text