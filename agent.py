import json
import boto3
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="ap-southeast-2"
)

polly = boto3.client(
    service_name="polly",
    region_name="ap-southeast-2"
)

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-southeast-2"
)

table = dynamodb.Table("CompassSessions")

with open("services.json") as f:
    services = json.load(f)

conversation_state = {
    "last_detected_service": None
}

def log_interaction(user_input, assistant_response, detected_services, final_recommendations=None):
    try:
        table.put_item(
            Item={
                "session_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "user_input": user_input,
                "assistant_reasoning": assistant_response,
                "detected_services": detected_services,
                "final_recommendations": final_recommendations or []
            }
        )
    except Exception as e:
        print("DynamoDB Error:", e)

def detect_service(user_input):
    user_input = user_input.lower()
    matched_services = []

    for key, service in services.items():
        for keyword in service["keywords"]:
            if keyword in user_input:
                matched_services.append(service)
                break

    return matched_services

def synthesize_speech(text):
    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Olivia",
            Engine="neural"
        )

        return response["AudioStream"].read()

    except Exception as e:
        print("Polly Error:", e)
        return None

def detect_service_with_bedrock(user_input):
    prompt = f"""
You are Compass, an empathetic and professional university student support navigation assistant.

Your goal is to:
- Reduce cognitive load for students
- Interpret their situation carefully
- Recommend only relevant services
- Maintain a calm, supportive tone

Analyse the student's message and determine which services apply.

Choose ONLY from:
- disability_support
- financial_aid
- counselling

Return ONLY valid JSON in this exact format:

{{
  "matched_services": ["service_key1", "service_key2"],
  "reasoning": "Brief, compassionate explanation of why these services were selected."
}}

Return JSON only.

Student message:
"{user_input}"
"""


    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(body)
    )

    response_body = json.loads(response["body"].read())
    text_output = response_body["content"][0]["text"]

    try:
        parsed = json.loads(text_output)
        return parsed

    except:
        return detect_service(user_input)



def generate_email(service, user_input):
    return f"""Subject: Request for Support

Dear {service['service_name']},

I hope you are well.

I am writing to seek advice regarding support, as I have {user_input}.
I would be grateful if you could please advise me on the available options and the documentation required to proceed with an application for assistance.
Thank you very much for your time and support.

Kind regards,
[Your Name]
"""

def generate_response(user_input):
    global conversation_state

    # Crisis detection
    crisis_keywords = [
        "suicidal",
        "self harm",
        "harm myself",
        "kill myself",
        "end my life"
    ]

    if any(keyword in user_input.lower() for keyword in crisis_keywords):
        return {
            "message": (
                "I'm really sorry that you're feeling this way. "
                "Your safety is important. Please consider reaching out to emergency services "
                "or contacting your university's crisis support service immediately. "
                "If you're in Australia, Lifeline is available on 13 11 14."
            )
        }
    
    # Confirmation Flow
    if conversation_state.get("last_detected_service"):

        if user_input.lower() in ["yes", "y"]:

            matched_services = conversation_state["last_detected_service"]

            recommended = []

            for index, service in enumerate(matched_services):
                confidence_score = round(0.95 - (index * 0.1), 2)

                recommended.append({
                    "service_name": service["service_name"],
                    "reason": service["reason_template"],
                    "contact": service["contact"],
                    "timeline": service["timeline"],
                    "next_steps": service["next_steps"],
                    "priority_rank": index + 1,
                    "confidence_score": confidence_score,
                    "confidence_level": "High" if confidence_score > 0.8 else "Moderate",
                    "email_draft": generate_email(
                        service,
                        conversation_state.get("original_user_input", "")
                    )
                })

            conversation_state["last_detected_service"] = None

            return {
                "message": "Thank you for sharing that. Based on what you've described, here are the support services that may be able to assist you:",
                "recommended_services": recommended
            }

        elif user_input.lower() in ["no", "n"]:

            conversation_state["last_detected_service"] = None

            return {
                "message": (
                    "Of course. Could you share a bit more about what you're currently struggling with — "
                    "such as financial concerns, academic pressure, or health-related issues?"
                )
            }

    # Initial Detection Flow
    bedrock_result = detect_service_with_bedrock(user_input)

    matched_keys = bedrock_result.get("matched_services", [])
    reasoning = bedrock_result.get("reasoning", "")

    matched_services = [services[key] for key in matched_keys if key in services]

    if matched_services:

        conversation_state["original_user_input"] = user_input
        conversation_state["last_detected_service"] = matched_services

        names = ", ".join([s["service_name"] for s in matched_services])

        return {
            "clarifying_question": f"{reasoning} I identified the following relevant services: {names}. Would you like more details?"
        }

    return {
        "message": "I'm sorry, I couldn't confidently match your concern to a specific service yet. Could you provide a little more detail?"
    }