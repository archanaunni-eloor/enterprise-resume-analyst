# Enterprise Resume Analyst AI

A robust, AI-powered Applicant Tracking System (ATS) built to bridge the gap between resumes and job descriptions using Generative AI.

## 🚀 Overview
The Enterprise Resume Analyst AI is a tool designed to help job seekers and recruiters optimize resumes against specific Job Descriptions (JD). By leveraging Google's Gemini 2.5 Flash model, it provides an instant match score and a comprehensive alignment analysis report.

## 🌟 Key Features
- **Intelligent ATS Scoring:** Calculates a match score out of 100 based on the JD alignment.
- **PDF Processing:** Seamlessly extracts text from PDF resumes.
- **Detailed Analysis:** Provides actionable feedback on how to improve the resume for specific roles.
- **Historical Tracking:** Logs all analysis reports in a persistent SQLite database.
- **Production Ready:** Securely handles API keys using environment variables.

## 🛠️ Tech Stack
- **Frontend/UI:** Streamlit
- **AI Model:** Google Gemini (Generative AI)
- **Data Management:** SQLite
- **PDF Processing:** pypdf
- **Deployment:** Streamlit Cloud

## 📋 Getting Started

### Prerequisites
- Python 3.9+
- A Google Gemini API Key (get it from [Google AI Studio](https://aistudio.google.com/))

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/archanaunni-eloor/
   cd archanaunni-eloor
Install dependencies:
pip install -r requirements.txt
Set your API Key (Environment Variable):

Linux/Mac: export GEMINI_API_KEY='your_api_key_here'

Windows: set GEMINI_API_KEY='your_api_key_here'

Run the application:
streamlit run app.py
Live Demo
Check out the live application here: https://enterprise-resume-analyst.streamlit.app

🤝 Contributing
Contributions are welcome! Please feel free to open an issue or submit a pull request if you have ideas to improve this tool.

👤 Author
Unni R

https://www.linkedin.com/in/unni-r-b09398a7/

https://github.com/archanaunni-eloor/
