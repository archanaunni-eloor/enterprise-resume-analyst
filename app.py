import streamlit as st
import requests

st.set_page_config(page_title="Resume Analyst AI GUI", page_icon="🤖")

st.title("🤖 Enterprise Resume Analyst AI")
st.markdown("---")

# 💻 സൈഡ്‌ബാർ നാവിഗേഷനോട് കൂടിയ ഹിസ്റ്ററി ലോജിക്
st.sidebar.header("📜 മുൻകാല ഹിസ്റ്ററി ലോഗ്")

# session_state-ൽ പേജ് നമ്പർ ഇനിഷ്യലൈസ് ചെയ്യുക
if "page_number" not in st.session_state:
    st.session_state.page_number = 0

try:
    response = requests.get("http://127.0.0.1:8000/history")
    if response.status_code == 200:
        all_history = response.json()
        
        if all_history:
            ITEMS_PER_PAGE = 5
            total_items = len(all_history)
            # ആകെ എത്ര പേജുകൾ ഉണ്ടെന്ന് കണക്കാക്കുന്നു
            total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            
            # കറന്റ് പേജിലെ 5 ലോഗുകൾ മാത്രം മുറിച്ചെടുക്കുന്നു
            start_idx = st.session_state.page_number * ITEMS_PER_PAGE
            end_idx = start_idx + ITEMS_PER_PAGE
            current_page_logs = all_history[start_idx:end_idx]
            
            # ഡാറ്റ കാണിക്കുന്നു
            for log in current_page_logs:
                st.sidebar.write(f"⏱️ **{log['timestamp']}**")
                st.sidebar.write(f"📄 {log['filename']}")
                st.sidebar.write(f"⭐ **Score: {log['score']}/100**")
                st.sidebar.markdown("---")
                
            # ⬅️ ➡️ പ്രീവിയസ് - നെക്സ്റ്റ് ബട്ടണുകൾ
            st.sidebar.write(f"Page {st.session_state.page_number + 1} of {total_pages}")
            col_prev, col_next = st.sidebar.columns(2)
            
            with col_prev:
                if st.button("⬅️ Previous", disabled=(st.session_state.page_number == 0)):
                    st.session_state.page_number -= 1
                    st.rerun()
                    
            with col_next:
                if st.button("Next ➡️", disabled=(st.session_state.page_number >= total_pages - 1)):
                    st.session_state.page_number += 1
                    st.rerun()
        else:
            st.sidebar.write("ലോഗുകൾ ഒന്നും ലഭ്യമായില്ല.")
    else:
        st.sidebar.write("⚠️ ഹിസ്റ്ററി ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")
except Exception:
    st.sidebar.write("🔌 ബാക്ക്-എൻഡ് സെർവർ കണക്ട് ചെയ്തിട്ടില്ല.")

# 📥 സ്റ്റെപ്പ് 1: ജോബ് ഡിസ്‌ക്രിപ്ഷൻ (JD) ഇൻപുട്ട് ബോക്സ്
st.subheader("💼 സ്റ്റെപ്പ് 1: ജോബ് ഡിസ്‌ക്രിപ്ഷൻ (JD) നൽകുക")
jd_input = st.text_area("കമ്പനിയുടെ ജോബ് ഡിസ്‌ക്രിപ്ഷൻ (Job Description) ഇവിടെ പേസ്റ്റ് ചെയ്യുക", height=200)

# 📥 സ്റ്റെപ്പ് 2: റെസ്യൂമെ അപ്‌ലോഡ് ബോക്സ്
st.subheader("📄 സ്റ്റെപ്പ് 2: റെസ്യൂമെ അപ്‌ലോഡ് ചെയ്യുക")
uploaded_file = st.file_uploader("ക്ലിക്ക് ചെയ്ത് PDF ഫയൽ തിരഞ്ഞെടുക്കുക", type=["pdf"])

if uploaded_file is not None and jd_input:
    if st.button("Analyze Resume 🚀"):
        with st.spinner("ജമിനി AI റസ്യൂമെയും ജോബ് ഡിസ്‌ക്രിപ്ഷനും തമ്മിൽ താരതമ്യം ചെയ്യുകയാണ്..."):
            try:
                backend_url = "http://127.0.0.1:8000/analyze"
                
                # ഫയലും ഒപ്പം യൂസർ ടൈപ്പ് ചെയ്ത JD ടെക്സ്റ്റും ഒന്നിച്ച് ബാക്കെൻഡിലേക്ക് അയക്കുന്നു
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"job_description": jd_input}
                
                response = requests.post(backend_url, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    analysis_text = result.get("analysis", "")
                    
                    # സ്കോർ വേർതിരിച്ചെടുക്കുന്ന ഭാഗം
                    score_display = "N/A"
                    if "SCORE:" in analysis_text:
                        try:
                            score_line = [line for line in analysis_text.split("\n") if "SCORE:" in line][0]
                            score_display = score_line.replace("SCORE:", "").strip()
                            analysis_text = analysis_text.replace(score_line, "").strip()
                        except Exception:
                            pass
                    
                    st.markdown("---")
                    st.balloons()
                    
                    # സ്കോർ ബോക്സ് കാണിക്കുന്നു
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric(label="🎯 Resume Match Score", value=score_display)
                    
                    st.markdown("### 📊 AI Analysis Report")
                    st.markdown(analysis_text if analysis_text else "റിപ്പോർട്ട് ലഭ്യമായില്ല.")
                    
                    # 🔄 പുതിയ അനാലിസിസ് കഴിഞ്ഞ ഉടൻ സൈഡ്‌ബാർ ഹിസ്റ്ററി റീഫ്രഷ് ചെയ്യാൻ ഒരു ട്രിഗർ
                    #st.rerun()
                    
                else:
                    st.error("ബാക്കെൻഡിൽ നിന്ന് ശരിയായ മറുപടി ലഭിച്ചില്ല.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
elif uploaded_file is not None and not jd_input:
    st.warning("⚠️ ദയവായി മുകളിൽ ജോബ് ഡിസ്‌ക്രിപ്ഷൻ കൂടി പേസ്റ്റ് ചെയ്യുക!")