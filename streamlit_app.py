import streamlit as st
import google.generativeai as genai
import json
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="ZNA AI Career Studio", layout="wide")

# Securely get your API Key (Set this in GitHub Secrets or Streamlit Cloud Secrets)
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("Please configure the GEMINI_API_KEY in your secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') # Using stable flash model

# --- SESSION STATE INITIALIZATION ---
if "resume_data" not in st.session_state:
    st.session_state.resume_data = None
if "logs" not in st.session_state:
    st.session_state.logs = ["LLM Engine connected.", "Ready for input."]

def add_log(text):
    st.session_state.logs.insert(0, text)
    st.session_state.logs = st.session_state.logs[:5]

# --- APP LOGIC ---
def call_gemini(prompt, system_instruction):
    full_prompt = f"{system_instruction}\n\nUser Input: {prompt}"
    response = model.generate_content(full_prompt)
    return response.text

# --- SIDEBAR ---
with st.sidebar:
    st.title("🚀 ZNA AI Studio")
    menu = st.radio("Navigate Workspace", ["Dashboard", "Resume Builder", "Cover Letter", "ATS Matcher"])
    st.divider()
    st.info("Status: Gemini 1.5 Flash Connected")

# --- DASHBOARD ---
if menu == "Dashboard":
    st.header("Overview Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Input Modes", "Dual (Auto/Man)")
    col2.metric("Status", "Online")
    col3.metric("ATS Scanner", "NLP Active")
    col4.metric("Model", "1.5 Flash")

    st.subheader("System Logs")
    for log in st.session_state.logs:
        st.caption(f"🕒 {log}")

# --- RESUME BUILDER ---
elif menu == "Resume Builder":
    st.header("Smart Resume Builder")
    
    with st.form("builder_form"):
        name = st.text_input("Full Name")
        title = st.text_input("Target Job Title")
        raw_text = st.text_area("Paste Experience/LinkedIn Data", height=200)
        submit = st.form_submit_button("Auto-Generate AI Resume")

    if submit:
        with st.spinner("ZNA Intelligence is processing..."):
            instr = "Output ONLY valid JSON. Include: fullName, targetTitle, experience (list of dicts with title, duration, description), skills (list)."
            result = call_gemini(raw_text, instr)
            try:
                # Clean JSON markdown if present
                clean_json = result.replace("```json", "").replace("```", "").strip()
                st.session_state.resume_data = json.loads(clean_json)
                add_log("Resume successfully parsed.")
                st.success("Resume Generated!")
            except:
                st.error("Failed to parse AI response. Try again.")

    if st.session_state.resume_data:
        data = st.session_state.resume_state = st.session_state.resume_data
        st.divider()
        st.subheader(data['fullName'])
        st.caption(data['targetTitle'])
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write("**Experience**")
            for exp in data.get('experience', []):
                st.write(f"**{exp['title']}** | {exp.get('duration', 'N/A')}")
                st.write(exp['description'])
        with c2:
            st.write("**Skills**")
            st.write(", ".join(data.get('skills', [])))

# --- ATS MATCHER ---
elif menu == "ATS Matcher":
    st.header("ATS Match Engine")
    if not st.session_state.resume_data:
        st.warning("Please build a resume first!")
    else:
        jd = st.text_area("Paste Job Description")
        if st.button("Run Deep Scan"):
            with st.spinner("Analyzing match..."):
                instr = "Compare resume and JD. Output JSON: {score: number, missingKeywords: [], suggestions: []}"
                result = call_gemini(f"Resume: {st.session_state.resume_data} \n JD: {jd}", instr)
                clean_json = result.replace("```json", "").replace("```", "").strip()
                analysis = json.loads(clean_json)
                
                st.metric("Match Score", f"{analysis['score']}%")
                st.subheader("Missing Keywords")
                st.write(", ".join(analysis['missingKeywords']))
                st.subheader("Suggestions")
                for s in analysis['suggestions']:
                    st.markdown(f"- {s}")
