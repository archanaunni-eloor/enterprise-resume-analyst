import streamlit as st
import google.generativeai as genai
import pypdf
import sqlite3
import re
import os
from datetime import datetime

# 🎨 1. Streamlit Page Configuration
st.set_page_config(page_title="Resume Analyst AI GUI", page_icon="🤖")

st.title("🤖 Enterprise Resume Analyst AI")
st.markdown("---")

# 🔒 2. Secure API Key Configuration (Fetched from Environment Variables)
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("🔑 API Key not found! Please set up your Streamlit Secrets.")

# 💾 3. SQLite Database Logic
def init_db():
    conn = sqlite3.connect("resume_analyzer.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            filename TEXT,
            score INTEGER,
            analysis_report TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_analysis(filename, score, report):
    conn = sqlite3.connect("resume_analyzer.db")
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO resume_logs (timestamp, filename, score, analysis_report) VALUES (?, ?, ?, ?)",
        (current_time, filename, score, report)
    )
    conn.commit()
    conn.close()

def get_all_history():
    try:
        conn = sqlite3.connect("resume_analyzer.db")
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, filename, score FROM resume_logs ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [{"timestamp": r[0], "filename": r[1], "score": r[2]} for r in rows]
    except Exception:
        return []

# Initialize the database table
init_db()

# 📄 4. Function to Extract Text from PDF
def extract_text_from_pdf(file):
    pdf_reader = pypdf.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# 🔍 5. Function to Parse Score from Gemini Response
def parse_score(analysis_text: str) -> int:
    try:
        match = re.search(r"SCORE:\s*\[?(\d+)\]?/100", analysis_text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0
    except Exception:
        return 0

# 💻 6. Sidebar Navigation and History Log UI
st.sidebar.header("📜 Historical Logs")

if "page_number" not in st.session_state:
    st.session_state.page_number = 0

all_history = get_all_history()

if all_history:
    ITEMS_PER_PAGE = 5
    total_items = len(all_history)
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    start_idx = st.session_state.page_number * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_page_logs = all_history[start_idx:end_idx]
    
    for log in current_page_logs:
        st.sidebar.write(f"⏱️ **{log['timestamp']}**")
        st.sidebar.write(f"📄 {log['filename']}")
        st.sidebar.write(f"⭐ **Score: {log['score']}/100**")
        st.sidebar.markdown("---")
        
    st.sidebar.write(f"Page {st.session_state.page_number + 1} of {total_pages}")
    col_prev, col_next = st.sidebar.columns(2)
    
    with col_prev:
        if st.button("⬅️ Previous", disabled=(st.session_state.page_number == 0)):
            st.session_state.page_number -= 1
            st.sidebar.empty()
            
    with col_next:
        if st.button("Next ➡️", disabled=(st.session_state.page_number >= total_pages - 1)):
            st.session_state.page_number += 1
            st.sidebar.empty()
else:
    st.sidebar.write("No historical logs available.")

# 📥 7. Main Screen UI (Step 1 & 2)
st.subheader("💼 Step 1: Provide Job Description (JD)")
jd_input = st.text_area("Paste the company's Job Description here", height=200)

st.subheader("📄 Step 2: Upload Resume")
uploaded_file = st.file_uploader("Click to browse and upload a PDF file", type=["pdf"])

if uploaded_file is not None and jd_input:
    if st.button("Analyze Resume 🚀"):
        with st.spinner("Gemini AI is analyzing the alignment between the resume and the job description..."):
            try:
                # 📄 Extracting text from file
                resume_text = extract_text_from_pdf(uploaded_file)
                
                system_prompt = f"""
                You are an expert ATS (Applicant Tracking System) and Resume Recruiter.
                Analyze the following Resume against the provided Job Description.
                
                At the very top of your response, you MUST provide a definitive match score out of 100 based on the job description alignment. Format it exactly like this as the first line of your response: SCORE: [XX]/100 (where XX is the numerical score). Do not add any text before this line.
                
                JOB DESCRIPTION:
                {jd_input}
                
                RESUME:
                {resume_text}
                """
                
                

                # 🤖 Running Gemini Model
                model = genai.GenerativeModel("models/gemini-2.0-flash") # 👈 ഇതും പരീക്ഷിക്കാവുന്നതാണ്
                response = model.generate_content(system_prompt)
                analysis_text = response.text
                
                # 📊 Parsing Score and Report
                match_score = parse_score(analysis_text)
                
                score_display = "N/A"
                if "SCORE:" in analysis_text:
                    try:
                        score_line = [line for line in analysis_text.split("\n") if "SCORE:" in line][0]
                        score_display = score_line.replace("SCORE:", "").strip()
                        analysis_text = analysis_text.replace(score_line, "").strip()
                    except Exception:
                        pass
                
                # 💾 Logging to Database
                log_analysis(uploaded_file.name, match_score, analysis_text)
                
                # 🎉 Displaying Results on UI
                st.markdown("---")
                st.balloons()
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label="🎯 Resume Match Score", value=score_display)
                
                st.markdown("### 📊 AI Analysis Report")
                st.markdown(analysis_text if analysis_text else "Analysis report could not be generated.")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
elif uploaded_file is not None and not jd_input:
    st.warning("⚠️ Please paste the Job Description above to proceed with the analysis!")
