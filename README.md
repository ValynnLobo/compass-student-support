## Compass — Intelligent Student Support Navigator

**Live Demo:** https://compass-student-support.streamlit.app/
Compass is an agentic AI system designed to help university students navigate complex support services with clarity, empathy, and actionable guidance.

Universities offer a wide range of academic, wellbeing, financial, and accessibility services. However, students often experience:

* Uncertainty about which services apply to them.
* Confusion around eligibility and documentation.
* Congitive overload eligibility and documentation.
* Delayed help-seeking due to fragmented information.

Compass addresses this by acting as a personalised navigation layer between students and university services.

---

## Key Features
* Lightweight student authentication.
* AI-powered triage using Amazon Bedrock (Claude 3 Haiku).
* Ranked recommendations with confidence scoring.
* Auto-generated professional email drafts.
* Text-to-Speech via Amazon Polly.
* Interaction logging via DynamoDB.
* Crisis keyword detection with safety redirection.
* Custom Streamlit UI aligned to Figma prototype.

---

## Architecture Overview

Compass leverages AWS-managed services to create a scalable and explainable system:

| Component | Purpose |
|-----------|----------|
| Amazon Bedrock | Natural language reasoning and classification |
| Amazon Polly | Text-to-speech accessibility |
| Amazon DynamoDB | Session logging |
| Streamlit | Frontend application |

## Safety

Compass includes:

* Crisis keyword detection.
* Escalation messaging.
* Lifeline redirection (AU: 13 11 14).
* Transparent reasoning for recommendations.
* Confidence scoring for explanability.

---

## Running Locally

### Install dependencies

```bash
pip install -r requirements.txt
```
### Configure AWS credentials
``` bash
aws configure
```
### Run the application
``` bash
streamlit run app.py
```
---

## Tech Stack

**Frontend**
- Streamlit
- Custom CSS styling (Figma-aligned UI)

**Backend**
- Python 3.14
- boto3 (AWS SDK)

**AI & Cloud Services**
- Amazon Bedrock (Claude 3 Haiku)
- Amazon Polly
- Amazon DynamoDB

---
## AWS Services Used

| Service | Purpose |
|----------|----------|
| Amazon Bedrock | Natural language reasoning and service classification |
| Amazon Polly | Text-to-speech for accessibility |
| Amazon DynamoDB | Session logging and interaction storage |
| AWS IAM | Secure service access management |

Compass leverages managed AWS services to enable scalable, secure, and explainable student support navigation.

---

## Demo Requirements
### Login Requirements
To access system, use: <br/>
**Email Format:** The email must end with '@university.edu'. <br/>
**Example valid email:** student@university.edu <br/>
**Student ID:** Any non-empty value is accepted in the MVP version. <br/>
**Example:** 123456

### Example Prompts
To test Compass, try entering: <br/>
**Academic / Wellbeing:** I'm feeling overwhelmed with exams and my anxiety is getting worse." <br/>
**Financial:** "I'm struggling to pay my tuition fees this semester."<br/>
**Accessibility:** "I have a visual impairment and need exam accommodations."<br/>
**Out-of-Scope Input:** "I want pizza."<br/>
**Crisis Escalation:** "I feel suicidal and don't know what to do."<br/>

You should see:
- Clarifying questions.
- Ranked recommendations.
- Confidence scores.
- Email draft generation.
- Text-to-speech support.

---

## Demo Context

Built as part of the AWS Diversity Hackathon to demonstrate scalable, explainable student service navigation.

### MVP Scope (Hackathon Version)

This implementation represents a functional Minimum Viable Product (MVP), including:

- Lightweight demo authentication (email domain check)
- Service classification using Amazon Bedrock (Claude 3 Haiku).
- Ranked recommendations with confidence scoring.
- Email draft generation.
- Text-to-speech responses via Amazon Polly.
- Interaction logging via Amazon DynamoDB.
- Crisis keyword detection and safety escalation.

The MVP focuses on validating:
- Feasibility of AI-powered triage.
- Explainability of recommendations.
- Accessibility via speech support.
- Responsible AI guardrails.

---

### Production-Level Considerations

A production-ready deployment would include:

- Secure university authentication (SSO / Cognito / IAM federation).
- Role-based access control (RBAC).
- Encrypted storage and structured audit logging.
- RAG-based knowledge integration with official service documentation.
- Model evaluation and monitoring.
- Bias testing and fairness audits.
- Rate limiting and cost controls.
- API gateway and backend service separation.
- CI/CD pipeline and infrastructure as code.

The current MVP is intentionally scoped for demonstration purposes while showcasing architectural extensibility toward a production-grade system.
