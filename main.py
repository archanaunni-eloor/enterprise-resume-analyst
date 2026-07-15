from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import pypdf
import os
import sqlite3
import re
from datetime import datetime

app = FastAPI()

# 🌐 Streamlit ഫ്രണ്ട്-എൻഡുമായി തടസ്സമില്ലാതെ കണക്ട് ചെയ്യാൻ CORS സെറ്റിങ്സ്
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API Key കോൺഫിഗറേഷൻ
genai.configure(api_key="AQ.Ab8RN6ICgvZqxJsIwXY-Pc5-Lwd9N0k-KxEoYVwbXdXXrz4WTw")

# 💾 1. SQLite ഡാറ്റാബേസും ടേബിളും ഇനിഷ്യലൈസ് ചെയ്യാനുള്ള ഫങ്ഷൻ
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

# ഡാറ്റാബേസ് റൺ ചെയ്യുമ്പോൾ തന്നെ ടേബിൾ ക്രിയേറ്റ് ചെയ്യും
init_db()

def extract_text_from_pdf(file: UploadFile):
    pdf_reader = pypdf.PdfReader(file.file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# 🔍 Gemini റെസ്പോൺസിൽ നിന്ന് സ്കോർ മാത്രം വേർതിരിച്ചെടുക്കാനുള്ള ഹെൽപ്പർ ഫങ്ഷൻ
def parse_score(analysis_text: str) -> int:
    try:
        # "SCORE: [XX]/100" എന്ന പാറ്റേൺ കോഡിൽ നിന്ന് കണ്ടെത്തുന്നു
        match = re.search(r"SCORE:\s*\[?(\d+)\]?/100", analysis_text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0  # സ്കോർ കണ്ടെത്താൻ പറ്റിയില്ലെങ്കിൽ ഡിഫോൾട്ട് 0
    except Exception:
        return 0

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        resume_text = extract_text_from_pdf(file)
        
        system_prompt = f"""
        You are an expert ATS (Applicant Tracking System) and Resume Recruiter.
        Analyze the following Resume against the provided Job Description.
        
        At the very top of your response, you MUST provide a definitive match score out of 100 based on the job description alignment. Format it exactly like this as the first line of your response: SCORE: [XX]/100 (where XX is the numerical score). Do not add any text before this line.
        
        JOB DESCRIPTION:
        {job_description}
        
        RESUME:
        {resume_text}
        """
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(system_prompt)
        analysis_text = response.text
        
        # 📊 2. Gemini റെസ്പോൺസിൽ നിന്ന് സ്കോർ പാഴ്സ് ചെയ്ത് എടുക്കുന്നു
        match_score = parse_score(analysis_text)
        filename = file.filename
        
        # 💾 3. ഡാറ്റാബേസിലേക്ക് അനാലിസിസ് ലോഗ് സേവ് ചെയ്യുന്നു
        conn = sqlite3.connect("resume_analyzer.db")
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO resume_logs (timestamp, filename, score, analysis_report) VALUES (?, ?, ?, ?)",
            (current_time, filename, match_score, analysis_text)
        )
        conn.commit()
        conn.close()
        
        return {"analysis": analysis_text}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# 📜 4. ഫ്രണ്ട്-എൻഡിന് (Streamlit) ഹിസ്റ്ററി കാണിച്ചു കൊടുക്കാനുള്ള പുതിയ എന്റ്പോയിന്റ്
@app.get("/history")
def get_history_logs():
    try:
        conn = sqlite3.connect("resume_analyzer.db")
        cursor = conn.cursor()
        # ഏറ്റവും പുതിയ 5 അനാലിസിസ് ഹിസ്റ്ററി മാത്രം എടുക്കുന്നു
        cursor.execute("SELECT timestamp, filename, score FROM resume_logs ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        # ഫ്രണ്ട്-എൻഡിലേക്ക് ലിസ്റ്റ് ഓഫ് ഡിക്‌ഷ്ണറി ആയി അയക്കുന്നു
        return [{"timestamp": r[0], "filename": r[1], "score": r[2]} for r in rows]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})