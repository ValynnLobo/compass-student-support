import streamlit as st
from agent import generate_response, synthesize_speech

st.set_page_config(page_title="Compass", layout="centered")

# GLOBAL STYLING
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0F172A !important;
}
.block-container {
    max-width: 600px;
    margin: auto;
    padding-top: 40px;
}
.compass-header {
    background: linear-gradient(135deg, #A9C6D9, #E6D48F);
    padding: 30px;
    border-radius: 28px;
    margin-bottom: 30px;
    color: #111827;
}
.compass-title {
    font-size: 28px;
    font-weight: 700;
}
.compass-sub {
    font-size: 14px;
    opacity: 0.85;
}
.user-bubble {
    background-color: #E6D48F;
    padding: 14px 18px;
    border-radius: 16px;
    color: #111827;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}
.assistant-bubble {
    background-color: #B9D9D3;
    padding: 14px 18px;
    border-radius: 16px;
    color: #111827;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}
div[data-testid="stTextInput"] input {
    background-color: #1E293B !important;
    color: white !important;
    border-radius: 20px !important;
    border: none !important;
    padding: 14px !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #94A3B8 !important;
}
.stButton>button {
    background-color: #E6D48F;
    color: #111827;
    border-radius: 14px;
    border: none;
    padding: 8px 14px;
}

div[data-testid="stFormSubmitButton"] > button {
    background-color: #E6D48F !important;
    color: #000000 !important;
    border-radius: 14px !important;
    border: none !important;
    padding: 8px 14px !important;
}

div[data-testid="stFormSubmitButton"] > button * {
    color: #000000 !important;
    fill: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# AUTHENTICATION
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.markdown("""
    <style>
    h1, h2, h3, label, p, span {
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Compass")
    st.markdown("### Secure Student Access Required")
    st.caption("Compass is available to enrolled university students only.")

    with st.form("login_form"):
        email = st.text_input("University Email")
        student_id = st.text_input("Student ID", type="password")
        login_clicked = st.form_submit_button("Login")

        if login_clicked:
            if email.endswith("@university.edu") and student_id:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access restricted to university students.")

    st.stop()

# HEADER
st.sidebar.success("Logged in as student")

st.markdown("""
<div class="compass-header">
    <div class="compass-title">🧭 Compass</div>
    <div class="compass-sub">
        Hi 👋 I'm Compass. I'm here to guide you to the right support — confidentially and step-by-step.
    </div>
</div>
""", unsafe_allow_html=True)


# FORMAT RESPONSE
def format_response(response):
    assistant_text = ""

    if "message" in response:
        assistant_text += response["message"] + "\n\n"

    if "recommended_services" in response:
        for service in response["recommended_services"]:
            assistant_text += f"""
### 📌 {service['service_name']}
**Priority:** #{service['priority_rank']}  
**Confidence:** {service['confidence_level']} ({service['confidence_score']})  

**Why recommended:** {service['reason']}  
**Contact:** {service['contact']}  
**Response time:** {service['timeline']}  
**Next steps:** {service['next_steps']}
"""

            if "email_draft" in service:
                assistant_text += f"""

**Draft Email:**
{service['email_draft']}
"""

    return assistant_text

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_confirmation" not in st.session_state:
    st.session_state.pending_confirmation = None

# DISPLAY MESSAGES
for i, msg in enumerate(st.session_state.messages):

    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble">{msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="assistant-bubble">{msg["content"]}</div>',
            unsafe_allow_html=True
        )

        if st.button("🔊", key=f"listen_{i}"):
            audio_bytes = synthesize_speech(msg["content"])
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")

# CHAT INPUT FORM
with st.form("chat_form", clear_on_submit=True):

    col1, col2 = st.columns([8, 1])

    with col1:
        user_prompt = st.text_input(
            "",
            placeholder="Describe what you need help with..."
        )

    with col2:
        send_clicked = st.form_submit_button("➤")

    if send_clicked and user_prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": user_prompt
        })

        response = generate_response(user_prompt)

        if "clarifying_question" in response:
            st.session_state.pending_confirmation = True
            st.session_state.last_response = response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["clarifying_question"]
            })
        else:
            formatted_text = format_response(response)
            st.session_state.messages.append({
                "role": "assistant",
                "content": formatted_text
            })

        st.rerun()

# CONFIRMATION BUTTONS
if st.session_state.pending_confirmation:

    col1, col2 = st.columns(2)

    if col1.button("Yes, show details"):
        detailed_response = generate_response("yes")
        formatted_text = format_response(detailed_response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": formatted_text
        })

        st.session_state.pending_confirmation = False
        st.rerun()

    if col2.button("No, clarify further"):
        clarify_response = generate_response("no")
        formatted_text = format_response(clarify_response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": formatted_text
        })

        st.session_state.pending_confirmation = False
        st.rerun()