import uuid
from huggingface_client import send_to_huggingface_api
from fastapi import  HTTPException
user_sessions = {}

def generate_session_id():
    return str(uuid.uuid4())

system_prompt = """
Consider me as a layman, a general person who doesn't have any knowledge of the medical field.
I have my medical report. What I would like from you is, I will give you the text of my report, 
which contains many complex medical terms that I can't understand. 
So I want you to read the report, analyze it, and then give me a simplified version.

The response should:
1. Start with a greeting.
2. List only abnormalities or issues, avoiding details about what is normal.
3. Use a structured format:
   - Findings and location:
   - Impression:
4. If the report is normal, state it happily and briefly.

Conclude with this disclaimer:
*"This report has been generated by artificial intelligence and is intended to provide a simplified explanation of your medical condition. However, it is always advisable to consult a healthcare professional for definitive diagnosis and treatment."*
"""


def simplify_report(report_text):
    full_input = system_prompt + "\n\n" + report_text
    simplified_report = send_to_huggingface_api([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": report_text}
    ])
    session_id = generate_session_id()
    user_sessions[session_id] = report_text
    return {"session_id": session_id, "simplified_report": simplified_report}

def handle_user_question(session_id, question):
    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    medical_report = user_sessions[session_id]
    question_input = f"Here is the medical report:\n\n{medical_report}\n\nQuestion: {question}"
    response = send_to_huggingface_api([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question_input}
    ])
    return response

def end_session(session_id):
    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    del user_sessions[session_id]
    return {"message": "Session ended and data cleared successfully."}