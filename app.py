import streamlit as st
import json
import os
import tempfile
import plotly.express as px
import pandas as pd
from translations import translations

from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="AI Coach Mastery",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Language Selector
st.sidebar.image("logo.jpg", width=200)
language = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"])
t = translations[language]

# --- AUTHENTICATION SYSTEM ---
import auth_handler
import firebase_config

# Initialize Firebase (for Firestore only)
if 'firebase_initialized' not in st.session_state:
    if firebase_config.initialize_firebase():
        st.session_state.firebase_initialized = True
    else:
        st.session_state.firebase_initialized = False

# Check if user is authenticated
if not auth_handler.is_authenticated():
    st.title("🔐 Login / تسجيل الدخول")
    
    tab1, tab2, tab3 = st.tabs([
        "Login / دخول", 
        "Sign Up / تسجيل جديد",
        "Forgot Password / نسيت كلمة المرور"
    ])
    
    with tab1:
        st.write("### Email & Password")
        with st.form("login_form"):
            email = st.text_input("Email / البريد الإلكتروني", key="login_email")
            password = st.text_input("Password / كلمة المرور", type="password", key="login_password")
            remember_me = st.checkbox("Remember me / تذكرني")
            submit_login = st.form_submit_button("🔓 Login / دخول", use_container_width=True, type="primary")
            
            if submit_login:
                if not email or not password:
                    st.error("Please fill all fields" if language == "English" else "الرجاء ملء جميع الحقول")
                else:
                    with st.spinner("Verifying..." if language == "English" else "جاري التحقق..."):
                        result = auth_handler.sign_in_with_email(email, password)
                        
                        if result.get("success"):
                            auth_handler.save_session(result)
                            st.success(f"Welcome back! / مرحباً بعودتك!")
                            st.rerun()
                        else:
                            error_msg = result.get("error", "Unknown error")
                            if "INVALID_PASSWORD" in error_msg or "INVALID_LOGIN_CREDENTIALS" in error_msg:
                                st.error("Invalid email or password" if language == "English" else "البريد الإلكتروني أو كلمة المرور غير صحيحة")
                            elif "USER_NOT_FOUND" in error_msg:
                                st.error("No account found with this email" if language == "English" else "لا يوجد حساب بهذا البريد")
                            else:
                                st.error(f"Error: {error_msg}")
    
    with tab2:
        st.write("### Create New Account")
        with st.form("signup_form"):
            new_email = st.text_input("Email / البريد الإلكتروني", key="signup_email")
            new_password = st.text_input("Password / كلمة المرور", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password / تأكيد كلمة المرور", type="password")
            submit_signup = st.form_submit_button("📝 Sign Up / تسجيل", use_container_width=True, type="primary")
            
            if submit_signup:
                if not new_email or not new_password or not confirm_password:
                    st.error("Please fill all fields" if language == "English" else "الرجاء ملء جميع الحقول")
                elif new_password != confirm_password:
                    st.error("Passwords do not match" if language == "English" else "كلمات المرور غير متطابقة")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters" if language == "English" else "يجب أن تكون كلمة المرور 6 أحرف على الأقل")
                else:
                    with st.spinner("Creating account..." if language == "English" else "جاري إنشاء الحساب..."):
                        result = auth_handler.sign_up_with_email(new_email, new_password)
                        
                        if result.get("success"):
                            # Also create user profile in Firestore
                            firebase_config.create_user(new_email, new_password, new_email.split('@')[0])
                            st.success("Account created successfully! Please login." if language == "English" else "تم إنشاء الحساب بنجاح! الرجاء تسجيل الدخول.")
                        else:
                            error_msg = result.get("error", "Unknown error")
                            if "EMAIL_EXISTS" in error_msg:
                                st.error("Email already exists" if language == "English" else "البريد الإلكتروني مستخدم بالفعل")
                            elif "WEAK_PASSWORD" in error_msg:
                                st.error("Password is too weak" if language == "English" else "كلمة المرور ضعيفة جداً")
                            else:
                                st.error(f"Error: {error_msg}")
    
    with tab3:
        st.write("### Reset Your Password")
        with st.form("reset_form"):
            reset_email = st.text_input("Email / البريد الإلكتروني", key="reset_email")
            submit_reset = st.form_submit_button("📧 Send Reset Link / إرسال رابط إعادة التعيين", use_container_width=True)
            
            if submit_reset:
                if not reset_email:
                    st.error("Please enter your email" if language == "English" else "الرجاء إدخال بريدك الإلكتروني")
                else:
                    with st.spinner("Sending email..." if language == "English" else "جاري الإرسال..."):
                        result = auth_handler.send_password_reset_email(reset_email)
                        
                        if result.get("success"):
                            st.success("Password reset email sent! Check your inbox." if language == "English" else "تم إرسال رابط إعادة التعيين! تحقق من بريدك.")
                        else:
                            error_msg = result.get("error", "Unknown error")
                            if "EMAIL_NOT_FOUND" in error_msg:
                                st.error("No account found with this email" if language == "English" else "لا يوجد حساب بهذا البريد")
                            else:
                                st.error(f"Error: {error_msg}")
    
    # Stop execution if not logged in
    st.stop()

# Logout Button in Sidebar
st.sidebar.markdown("---")
st.sidebar.write(f"👤 **{st.session_state.user_email}**")
if st.sidebar.button("🚪 Logout / خروج"):
    auth_handler.clear_session()
    st.rerun()
st.sidebar.markdown("---")

# Custom CSS for Branding
st.markdown("""
    <style>
    /* Main Background - Dark Navy */
    .stApp {
        background-color: #050A14;
        color: #F5F5DC;
    }
    
    /* Sidebar Background - Slightly Lighter Navy */
    [data-testid="stSidebar"] {
        background-color: #0A1424;
    }
    
    /* Text Colors - Beige/Cream */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #F5F5DC !important;
    }
    
    /* Accent Color - Orange (Buttons & Highlights) */
    .stButton > button {
        background-color: #FF4500 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #FF6326 !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background-color: #1C2A40;
        color: white;
        border: 1px solid #FF4500;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0A1424;
        border-radius: 4px;
        color: #F5F5DC;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4500 !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1C2A40;
        color: #F5F5DC;
    }
    
    /* RTL Support for Arabic */
    .stApp {
        direction: %s;
    }
    </style>
    """ % ("rtl" if language == "العربية" else "ltr"), unsafe_allow_html=True)

# Load Markers
@st.cache_data
def load_markers():
    try:
        with open('markers.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("markers.json not found!")
        return None

markers_data = load_markers()

# Sidebar Inputs
# api_key = st.sidebar.text_input(t["enter_api_key"], type="password") # Removed
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.sidebar.error("⚠️ API Key not found in .env file")

mode = st.sidebar.radio(t["select_mode"], [t["mode_training"], t["mode_exam"], t["mode_profile"]])

# Helper: Radar Chart
def plot_radar_chart(analysis_result):
    data = []
    for comp in analysis_result.get('competencies', []):
        total = len(comp['markers'])
        observed = sum(1 for m in comp['markers'] if m['status'] == "OBSERVED")
        score = (observed / total) * 100 if total > 0 else 0
        data.append(dict(Competency=comp['id'], Score=score, Name=comp.get('name', comp['id'])))
    
    df = pd.DataFrame(data)
    fig = px.line_polar(df, r='Score', theta='Competency', line_close=True, 
                        title="Competency Balance" if language=="English" else "توازن الجدارات",
                        range_r=[0, 100])
    fig.update_traces(fill='toself')
    return fig

# Main Content
st.title(t["title"])

# --- TRAINING MODE ---
if mode == t["mode_training"]:
    st.header(t["training_header"])
    st.write(t["training_desc"])
    
    # Unified File Uploader
    uploaded_file = st.file_uploader(
        t["upload_label"], 
        type=['mp3', 'wav', 'm4a', 'txt', 'pdf', 'docx', 'rtf']
    )
    
    is_audio = False
    transcript_text = ""
    
    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        if file_type in ['mp3', 'wav', 'm4a']:
            is_audio = True
            st.audio(uploaded_file)
        else:
            is_audio = False
            try:
                if file_type == 'pdf':
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        transcript_text += page.extract_text() + "\n"
                elif file_type == 'docx':
                    import docx
                    doc = docx.Document(uploaded_file)
                    for para in doc.paragraphs:
                        transcript_text += para.text + "\n"
                elif file_type == 'rtf':
                    from striprtf.striprtf import rtf_to_text
                    rtf_content = uploaded_file.read().decode("utf-8", errors="ignore")
                    transcript_text = rtf_to_text(rtf_content)
                else: # txt
                    transcript_text = str(uploaded_file.read(), "utf-8")
            except Exception as e:
                st.error(f"Error reading file: {e}")
            
            if transcript_text:
                st.text_area(t["preview"], transcript_text, height=150)

    if uploaded_file:
        # Initialize session state for analysis if not present
        if 'analysis_result' not in st.session_state:
            st.session_state.analysis_result = None
        if 'ethics_result' not in st.session_state:
            st.session_state.ethics_result = None
            
        # Analyze Button
        if st.button(t["analyze_btn"]):
            if not api_key:
                st.error(t["enter_api_key"])
            else:
                from analysis_engine import AnalysisEngine
                engine = AnalysisEngine(api_key, markers_data)
                
                gemini_file = None
                content_to_analyze = None
                
                try:
                    if is_audio:
                        with st.spinner(t["processing_audio"]):
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
                                tmp.write(uploaded_file.getvalue())
                                tmp_path = tmp.name
                            
                            gemini_file = engine.upload_audio(tmp_path, mime_type=uploaded_file.type)
                            content_to_analyze = gemini_file
                            st.success(t["audio_success"])
                            os.unlink(tmp_path)
                    else:
                        # Use the text extracted during upload preview
                        content_to_analyze = transcript_text

                    # 1. Ethical Check
                    with st.spinner(t["checking_ethics"]):
                        st.session_state.ethics_result = engine.check_ethics(content_to_analyze, is_audio=is_audio, language=language)
                    
                    # 2. Marker Analysis (only if ethics pass or we want to show anyway, but usually we stop)
                    if st.session_state.ethics_result.get("status") != "FAIL":
                        with st.spinner(t["analyzing_markers"]):
                            st.session_state.analysis_result = engine.analyze_markers(content_to_analyze, is_audio=is_audio, language=language)
                            st.session_state.analysis_result['ethics_status'] = st.session_state.ethics_result.get("status", "UNKNOWN")
                    else:
                        st.session_state.analysis_result = None # Clear previous analysis if ethics fail

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        
        # Display Results (from Session State)
        if st.session_state.ethics_result:
            ethics_result = st.session_state.ethics_result
            if ethics_result.get("status") == "FAIL":
                st.error(t["ethics_fail"])
                st.write(f"**Reason:** {ethics_result.get('reason')}")
            elif ethics_result.get("status") == "ERROR":
                st.error(f"Error: {ethics_result.get('reason')}")
            else:
                st.success(t["ethics_pass"])
                
                if st.session_state.analysis_result:
                    analysis_result = st.session_state.analysis_result
                    
                    if "error" in analysis_result:
                        st.error(f"Analysis Error: {analysis_result['error']}")
                    else:
                        st.success(t["analysis_complete"])
                        
                        # --- MCC EXECUTIVE DASHBOARD ---
                        st.markdown("## 🎯 MCC Session Audit / تدقيق جلسة MCC")
                        
                        # 1. Top Metrics Row (4 Columns)
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            overall_score = analysis_result.get('overall_score', 6.0)
                            st.metric("📊 Overall Score / النتيجة", f"{overall_score:.1f}/10")
                        
                        with col2:
                            talk_ratio = analysis_result.get('talk_ratio', 'N/A')
                            st.metric("🗣️ Talk Ratio / نسبة التحدث", talk_ratio)
                        
                        with col3:
                            silence = analysis_result.get('silence_count', 0)
                            st.metric("🤫 Silence / الصمت", f"{silence}")
                        
                        with col4:
                            ethics = analysis_result.get('ethics_status', 'PASS')
                            ethics_icon = "✅" if ethics != "FAIL" else "❌"
                            st.metric("⚖️ Ethics / الأخلاقيات", f"{ethics_icon} {ethics}")
                        
                        st.markdown("---")

                        # 2. Visual Centerpiece - Radar Chart
                        competencies_dict = analysis_result.get('competencies', {})
                        
                        if competencies_dict:
                            # Prepare radar chart data
                            radar_data = []
                            for comp_id, comp_data in competencies_dict.items():
                                radar_data.append({
                                    'Competency': comp_id,
                                    'Score': comp_data.get('score', 0),
                                    'Name': comp_data.get('name', comp_id)
                                })
                            
                            df_radar = pd.DataFrame(radar_data)
                            
                            fig_radar = px.line_polar(
                                df_radar, 
                                r='Score', 
                                theta='Competency', 
                                line_close=True,
                                title="Competency Balance / توازن الجدارات",
                                range_r=[0, 10],
                                hover_data=['Name']
                            )
                            fig_radar.update_traces(fill='toself', fillcolor='rgba(63, 81, 181, 0.3)')
                            fig_radar.update_layout(
                                polar=dict(
                                    radialaxis=dict(
                                        visible=True,
                                        range=[0, 10],
                                        tickmode='linear',
                                        tick0=0,
                                        dtick=2
                                    )
                                ),
                                showlegend=False,
                                height=500
                            )
                            
                            st.plotly_chart(fig_radar, use_container_width=True)
                            
                            # Save radar chart for PDF
                            try:
                                fig_radar.write_image("radar_chart.png")
                            except Exception as e:
                                st.warning(f"Could not save chart for PDF: {e}")
                        
                        st.markdown("---")

                        # 3. Detailed Analysis (Enhanced Accordions with Color Coding)
                        st.subheader("📚 Detailed Competency Analysis / التحليل التفصيلي")
                        
                        if competencies_dict:
                            for comp_id, comp_data in competencies_dict.items():
                                comp_name = comp_data.get('name', comp_id)
                                comp_score = comp_data.get('score', 0)
                                
                                with st.expander(f"{comp_id}: {comp_name} - {comp_score:.1f}/10", expanded=False):
                                    # Progress bar
                                    st.progress(comp_score / 10)
                                    
                                    # Markers
                                    for marker in comp_data.get('markers', []):
                                        marker_id = marker.get('id', '')
                                        status = marker.get('status', 'Fail')
                                        evidence = marker.get('evidence', 'N/A')
                                        auditor_note = marker.get('auditor_note', '')
                                        
                                        if status == 'Pass':
                                            # Green success box
                                            st.success(f"**✅ Marker {marker_id}**: Pass")
                                            st.write(f"**Evidence:** {evidence}")
                                            st.caption(f"**Auditor Note:** {auditor_note}")
                                        else:
                                            # Red failure box
                                            st.error(f"**❌ Marker {marker_id}**: Fail")
                                            st.write(f"**Missing Evidence**")
                                            st.caption(f"**Auditor Critique:** {auditor_note}")
                                        
                                        st.markdown("---")
                        
                        # 4. PDF Generation using ReportLab
                        from pdf_renderer import generate_mcc_pdf
                        
                        if st.button("📄 Download MCC Audit Report / تحميل تقرير التدقيق"):
                            try:
                                # Add ethics_status to result for PDF
                                analysis_result['ethics_status'] = st.session_state.ethics_result.get('status', 'PASS') if st.session_state.ethics_result else 'PASS'
                                
                                # Generate PDF
                                radar_path = "radar_chart.png" if os.path.exists("radar_chart.png") else None
                                pdf_bytes = generate_mcc_pdf(
                                    analysis_result, 
                                    language=language,
                                    radar_chart_path=radar_path
                                )
                                
                                st.download_button(
                                    label="📥 Click to Download PDF / اضغط للتحميل",
                                    data=pdf_bytes,
                                    file_name="mcc_audit_report.pdf",
                                    mime="application/pdf"
                                )
                            except Exception as e:
                                st.error(f"PDF Generation Error: {e}")


# --- TRAINING GYM (ADVANCED SIMULATOR) ---
elif mode == t["mode_exam"]:
    st.header(t["exam_header"])
    st.write("🎯 Advanced Coaching Lab / صالة التدريب المتقدمة" if language == "English" else "🎯 صالة التدريب المتقدمة")
    
    # Initialize Training Session States
    if 'training_mode' not in st.session_state:
        st.session_state.training_mode = "rephrase"  # rephrase, client_sim, full_session
    if 'current_challenge' not in st.session_state:
        st.session_state.current_challenge = None
    if 'rephrase_result' not in st.session_state:
        st.session_state.rephrase_result = None
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'current_draft_response' not in st.session_state:
        st.session_state.current_draft_response = ""
    if 'client_persona' not in st.session_state:
        st.session_state.client_persona = "resistant"
    if 'mentor_feedback' not in st.session_state:
        st.session_state.mentor_feedback = {}
    if 'last_audio_hash' not in st.session_state:
        st.session_state.last_audio_hash = None
    if 'audio_input_key' not in st.session_state:
        st.session_state.audio_input_key = 0
    
    # Level 3: Full Session Simulator States
    if 'full_session_active' not in st.session_state:
        st.session_state.full_session_active = False
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = None
    if 'session_messages' not in st.session_state:
        st.session_state.session_messages = []
    if 'hidden_analyses' not in st.session_state:
        st.session_state.hidden_analyses = []  # Store all background analyses
    if 'session_phase' not in st.session_state:
        st.session_state.session_phase = 'not_started'  # not_started, opening, exploration, deepening, closing, ended
    if 'final_session_report' not in st.session_state:
        st.session_state.final_session_report = None
    if 'session_client_persona' not in st.session_state:
        st.session_state.session_client_persona = "resistant"
    if 'session_client_topic' not in st.session_state:
        st.session_state.session_client_topic = "career"
    
    # Mode Selection
    training_mode_label = "Select Training Level / اختر مستوى التدريب"
    mode_a_label = "Level 1: Re-Phrase Challenge / التحدي: إعادة الصياغة"
    mode_b_label = "Level 2: Difficult Client Simulator / محاكي العميل الصعب"
    mode_c_label = "Level 3: Full Coaching Session / جلسة تدريب كاملة"
    
    selected_mode = st.selectbox(
        training_mode_label,
        [mode_a_label, mode_b_label, mode_c_label],
        key="training_mode_selector"
    )
    
    st.markdown("---")
    
    # MODE A: RE-PHRASE CHALLENGE
    if mode_a_label in selected_mode:
        st.subheader("🔄 Re-Phrase Challenge")
        st.write("Transform bad coaching questions into powerful ones!" if language == "English" else "حوّل الأسئلة السيئة إلى أسئلة قوية!")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🎲 Generate New Challenge / توليد تحدي جديد", use_container_width=True):
                if not api_key:
                    st.error("Please enter API Key" if language == "English" else "الرجاء إدخال API Key")
                else:
                    from training_engine import TrainingEngine
                    trainer = TrainingEngine(api_key, markers_data)
                    with st.spinner("Generating..." if language == "English" else "جاري التوليد..."):
                        st.session_state.current_challenge = trainer.generate_bad_question(language=language)
                        st.session_state.current_draft_response = ""
        
        with col2:
            if st.button("🔄 Reset / إعادة تعيين", use_container_width=True):
                st.session_state.current_challenge = None
                if 'rephrase_textarea_value' in st.session_state:
                    del st.session_state.rephrase_textarea_value
                if 'transcribed_text' in st.session_state:
                    del st.session_state.transcribed_text
                st.session_state.rephrase_result = None
                st.session_state.last_audio_hash = None
                st.session_state.audio_input_key += 1  # Force audio input to reset
        
        if st.session_state.current_challenge:
            if 'error' in st.session_state.current_challenge:
                st.error(f"⚠️ {st.session_state.current_challenge.get('error', 'Failed to generate challenge.')}")
            else:
                challenge = st.session_state.current_challenge
                
                # Display the bad question
                st.error(f"**❌ Bad Question:**\n\n{challenge.get('bad_question', '')}")
                
                with st.expander("💡 Why is this bad? / لماذا هذا سيء؟", expanded=False):
                    st.write(challenge.get('what_makes_it_bad', ''))
                    st.caption(f"**Violates Marker:** {challenge.get('marker_violated', '')}")
                
                st.markdown("---")
                
                # Voice-to-Text Recording Section
                st.write("### 🎤 Voice Input (Optional) / الإدخال الصوتي (اختياري)")
                
                audio_input = st.audio_input(
                    "Record your answer / سجل إجابتك",
                    key=f"rephrase_audio_{st.session_state.audio_input_key}"
                )
                
                # Initialize transcribed_text in session state
                if 'transcribed_text' not in st.session_state:
                    st.session_state.transcribed_text = ""
                
                if audio_input:
                    audio_hash = hash(audio_input.getvalue())
                    if audio_hash != st.session_state.last_audio_hash:
                        st.session_state.last_audio_hash = audio_hash
                        try:
                            with st.spinner("Transcribing..." if language == "English" else "جاري النسخ..."):
                                from training_engine import TrainingEngine
                                trainer = TrainingEngine(api_key, markers_data)
                                transcript = trainer.transcribe_audio(audio_input, language=language)
                                
                                # Check if transcription failed
                                if "error" in transcript.lower() or "خطأ" in transcript:
                                    st.error(transcript)
                                    st.session_state.transcribed_text = ""
                                else:
                                    st.session_state.transcribed_text = transcript
                                    st.success("✅ Transcribed! Edit below if needed." if language == "English" else "✅ تم النسخ! عدل بالأسفل إذا لزم الأمر.")
                        except Exception as e:
                            st.error(f"Transcription failed: {str(e)}" if language == "English" else f"فشل النسخ: {str(e)}")
                            st.session_state.transcribed_text = ""
            
            # Show transcribed text in editable area if available
            if st.session_state.get('transcribed_text', ''):
                st.write("**📝 Transcribed Text (Edit if needed) / النص المنسوخ (عدل إذا لزم الأمر):**")
                edited_transcript = st.text_area(
                    "Transcribed text / النص المنسوخ",
                    value=st.session_state.transcribed_text,
                    height=100,
                    key="transcript_editor_rephrase",
                    label_visibility="collapsed"
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✅ Use this text / استخدم هذا النص", use_container_width=True, type="primary", key="use_text_rephrase_btn"):
                        # Delete the key if exists, then store the text for next rerun
                        if 'rephrase_textarea_value' in st.session_state:
                            del st.session_state.rephrase_textarea_value
                        st.session_state['_pending_rephrase_text'] = edited_transcript
                        st.rerun()
                with col2:
                    if st.button("🗑️ Clear / مسح", use_container_width=True, key="clear_rephrase_transcript_btn"):
                        if 'transcribed_text' in st.session_state:
                            del st.session_state.transcribed_text
                        if 'last_audio_hash' in st.session_state:
                            del st.session_state.last_audio_hash
                        st.rerun()
            
            st.markdown("---")
            
            # Initialize rephrase_textarea_value if not exists
            if 'rephrase_textarea_value' not in st.session_state:
                # Check if there's pending text from "Use this text" button
                if '_pending_rephrase_text' in st.session_state:
                    st.session_state.rephrase_textarea_value = st.session_state._pending_rephrase_text
                    del st.session_state._pending_rephrase_text
                else:
                    st.session_state.rephrase_textarea_value = ""
            
            # Editable text area (separate from voice)
            st.write("### ⌨️ Your Rewrite / إعادة صياغتك")
            user_rewrite = st.text_area(
                "Type your rewrite OR use transcribed text above / اكتب إعادة الصياغة أو استخدم النص المنسوخ أعلاه",
                height=120,
                key="rephrase_textarea_value",
                placeholder="Write your improved version here... / اكتب النسخة المحسّنة هنا..."
            )
            
            if st.button("📝 Submit for Grading / إرسال للتقييم", type="primary"):
                # Use the value from session_state
                user_rewrite_text = st.session_state.get('rephrase_textarea_value', '')
                
                if not user_rewrite_text.strip():
                    st.warning("Please write your rewrite first" if language == "English" else "الرجاء كتابة إعادة الصياغة أولاً")
                elif not api_key:
                    st.error("Please enter API Key" if language == "English" else "الرجاء إدخال API Key")
                else:
                    from training_engine import TrainingEngine
                    trainer = TrainingEngine(api_key, markers_data)
                    with st.spinner("Grading..." if language == "English" else "جاري التقييم..."):
                        result = trainer.evaluate_rephrase(
                            challenge.get('bad_question', ''),
                            user_rewrite_text,
                            challenge.get('marker_violated', ''),
                            language=language
                        )
                        st.session_state.rephrase_result = result
                        
                        # Save to Firebase
                        if auth_handler.is_authenticated():
                            import datetime
                            session_data = {
                                'user_id': st.session_state.user_id,
                                'session_type': 'Re-Phrase Challenge',
                                'score': result.get('score', 0),
                                'duration': "N/A",
                                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                'report_json': result
                            }
                            firebase_config.save_session(st.session_state.user_id, session_data)
            
            # Display results
            if st.session_state.get('rephrase_result') and 'error' not in st.session_state.rephrase_result:
                result = st.session_state.rephrase_result
                score = result.get('score', 0)
                
                st.markdown("---")
                st.subheader("📊 Your Results / نتائجك")
                
                # Score with color coding
                if score >= 7:
                    st.success(f"### 🌟 Score: {score}/10")
                elif score >= 4:
                    st.warning(f"### ⚠️ Score: {score}/10")
                else:
                    st.error(f"### ❌ Score: {score}/10")
                
                # Feedback
                st.info(f"**Feedback:**\n\n{result.get('feedback', '')}")
                
                # Master version
                with st.expander("✨ Master Coach Version / نسخة المدرب الخبير", expanded=True):
                    st.success(result.get('master_version', ''))
    
    # MODE C: FULL COACHING SESSION
    elif mode_c_label in selected_mode:
        st.subheader("🎓 Full Coaching Session Simulator")
        st.write("Conduct a complete 30-45 minute coaching session from start to finish!" if language == "English" else "قم بإجراء جلسة تدريب كاملة من البداية إلى النهاية!")
        
        # Session not started - Show configuration
        if not st.session_state.full_session_active:
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                persona_options = {
                    "resistant": "🛡️ Resistant" if language == "English" else "🛡️ مقاوم",
                    "looping": "🔄 Looping" if language == "English" else "🔄 متكرر",
                    "emotional": "😢 Emotional" if language == "English" else "😢 عاطفي",
                    "analytical": "🤔 Analytical" if language == "English" else "🤔 تحليلي",
                    "urgent": "⚡ Urgent" if language == "English" else "⚡ عجول"
                }
                
                selected_persona_label = st.selectbox(
                    "Client Persona / شخصية العميل",
                    list(persona_options.values())
                )
                st.session_state.session_client_persona = [k for k, v in persona_options.items() if v == selected_persona_label][0]
            
            with col2:
                topic_options = {
                    "family": "👨‍👩‍👧‍👦 Family" if language == "English" else "👨‍👩‍👧‍👦 العائلة",
                    "career": "💼 Career" if language == "English" else "💼 المهنة",
                    "relationships": "💑 Relationships" if language == "English" else "💑 العلاقات",
                    "finance": "💰 Finance" if language == "English" else "💰 المال",
                    "life_goals": "🎯 Life Goals" if language == "English" else "🎯 أهداف الحياة",
                    "emotions": "😰 Stress/Emotions" if language == "English" else "😰 التوتر/المشاعر",
                    "balance": "⚖️ Work-Life Balance" if language == "English" else "⚖️ التوازن",
                    "growth": "🎓 Personal Growth" if language == "English" else "🎓 النمو الشخصي"
                }
                
                selected_topic_label = st.selectbox(
                    "Topic / الموضوع",
                    list(topic_options.values())
                )
                st.session_state.session_client_topic = [k for k, v in topic_options.items() if v == selected_topic_label][0]
            
            with col3:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("🎬 Start Session / ابدأ الجلسة", use_container_width=True, type="primary"):
                    import datetime
                    st.session_state.full_session_active = True
                    st.session_state.session_start_time = datetime.datetime.now()
                    st.session_state.session_messages = []
                    st.session_state.hidden_analyses = []
                    st.session_state.session_phase = 'opening'
                    st.session_state.final_session_report = None
                    st.rerun()
            
            st.info("💡 Tip: This is a full coaching session. Take your time, use powerful questions, and let the client lead!" if language == "English" else "💡 نصيحة: هذه جلسة تدريب كاملة. خذ وقتك، استخدم أسئلة قوية، ودع العميل يقود!")
        
        # Session active - Show session interface
        else:
            import datetime
            
            # Calculate session duration
            elapsed = datetime.datetime.now() - st.session_state.session_start_time
            elapsed_minutes = int(elapsed.total_seconds() / 60)
            elapsed_seconds = int(elapsed.total_seconds() % 60)
            
            # Header with timer and stats
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                st.metric("⏱️ Time", f"{elapsed_minutes:02d}:{elapsed_seconds:02d}")
            
            with col2:
                st.metric("💬 Exchanges", len([m for m in st.session_state.session_messages if m['role'] == 'Coach']))
            
            with col3:
                phase_emoji = {"opening": "📂", "exploration": "🔍", "deepening": "💎", "closing": "🎯"}
                phase_name = st.session_state.session_phase.title()
                st.metric("📊 Phase", f"{phase_emoji.get(st.session_state.session_phase, '📊')} {phase_name}")
            
            with col4:
                if st.button("⏹️ End Session", use_container_width=True, type="secondary"):
                    # Generate comprehensive final report
                    st.session_state.session_phase = 'ended'
                    st.session_state.full_session_active = False
                    
                    with st.spinner("Analyzing complete session..." if language == "English" else "جاري تحليل الجلسة الكاملة..."):
                        from training_engine import TrainingEngine
                        trainer = TrainingEngine(api_key, markers_data)
                        
                        # Generate comprehensive report
                        st.session_state.final_session_report = trainer.analyze_full_coaching_session(
                            st.session_state.session_messages,
                            st.session_state.hidden_analyses,
                            elapsed_minutes,
                            language=language
                        )
                        
                        # Save to Firebase
                        if auth_handler.is_authenticated():
                            session_data = {
                                'user_id': st.session_state.user_id,
                                'session_type': 'Full Session',
                                'score': st.session_state.final_session_report.get('overall_score', 0),
                                'duration': f"{elapsed_minutes} min",
                                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                'report_json': st.session_state.final_session_report
                            }
                            firebase_config.save_session(st.session_state.user_id, session_data)
                    
                    st.rerun()
            
            st.markdown("---")
            
            # Display conversation
            for msg in st.session_state.session_messages:
                role = msg.get('role', '')
                content = msg.get('content', '')
                
                if role == 'Client':
                    with st.chat_message("user", avatar="🧑"):
                        st.write(f"**Client:** {content}")
                elif role == 'Coach':
                    with st.chat_message("assistant", avatar="🎯"):
                        st.write(f"**You (Coach):** {content}")
            
            st.markdown("---")
            
            # Coach input
            if 'session_coach_textarea_value' not in st.session_state:
                st.session_state.session_coach_textarea_value = ""
            
            st.write("### Your Coaching Response / ردك التدريبي")
            coach_response = st.text_area(
                "Type your coaching question or response / اكتب سؤالك أو ردك التدريبي",
                height=100,
                key="session_coach_textarea_value",
                placeholder="What would you like to explore with the client? / ماذا تريد استكشافه مع العميل؟"
            )
            
            if st.button("📤 Send / إرسال", type="primary"):
                if not coach_response.strip():
                    st.warning("Please type your response" if language == "English" else "الرجاء كتابة ردك")
                elif not api_key:
                    st.error("Please enter API Key" if language == "English" else "الرجاء إدخال API Key")
                else:
                    with st.spinner("Processing..." if language == "English" else "جاري المعالجة..."):
                        from training_engine import TrainingEngine
                        trainer = TrainingEngine(api_key, markers_data)
                        
                        # Add coach message
                        st.session_state.session_messages.append({
                            'role': 'Coach',
                            'content': coach_response,
                            'timestamp': f"{elapsed_minutes:02d}:{elapsed_seconds:02d}",
                            'phase': st.session_state.session_phase
                        })
                        
                        # Background analysis (hidden from user during session)
                        analysis = trainer.evaluate_coach_response(
                            st.session_state.session_messages,
                            coach_response,
                            language=language
                        )
                        
                        # Store analysis with message index
                        st.session_state.hidden_analyses.append({
                            'message_index': len(st.session_state.session_messages) - 1,
                            'coach_message': coach_response,
                            'timestamp': f"{elapsed_minutes:02d}:{elapsed_seconds:02d}",
                            'phase': st.session_state.session_phase,
                            'analysis': analysis
                        })
                        
                        # Get phase-aware client response
                        client_response = trainer.simulate_full_session_client(
                            st.session_state.session_client_persona,
                            st.session_state.session_client_topic,
                            st.session_state.session_messages,
                            st.session_state.session_phase,
                            elapsed_minutes,
                            language=language
                        )
                        
                        if 'error' not in client_response:
                            st.session_state.session_messages.append({
                                'role': 'Client',
                                'content': client_response.get('client_response', 'I see...'),
                                'timestamp': f"{elapsed_minutes:02d}:{(elapsed_seconds+5):02d}"
                            })
                        
                        # Update phase based on time
                        if elapsed_minutes < 5:
                            st.session_state.session_phase = 'opening'
                        elif elapsed_minutes < 15:
                            st.session_state.session_phase = 'exploration'
                        elif elapsed_minutes < 30:
                            st.session_state.session_phase = 'deepening'
                        else:
                            st.session_state.session_phase = 'closing'
                        
                        # Clear input
                        if 'session_coach_textarea_value' in st.session_state:
                            del st.session_state.session_coach_textarea_value
                        st.rerun()
        
        #Show final report if session ended
        if st.session_state.final_session_report and not st.session_state.full_session_active:
            st.success("✅ Session Complete!" if language == "English" else "✅ الجلسة اكتملت!")
            
            report = st.session_state.final_session_report
            
            if 'error' not in report:
                # Header metrics
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    score = report.get('overall_score', 0)
                    if score >= 7:
                        st.success(f"### 🌟 Overall Score: {score}/10")
                    elif score >= 4:
                        st.warning(f"### ⚠️ Overall Score: {score}/10")
                    else:
                        st.error(f"### ❌ Overall Score: {score}/10")
                
                with col2:
                    st.metric("⏱️ Duration", report.get('session_duration', 'N/A'))
                
                with col3:
                    st.metric("💬 Exchanges", report.get('total_exchanges', 0))
                
                st.markdown("---")
                
                # Talk Ratio
                st.write("### 📊 Talk Ratio / نسبة الحديث")
                st.info(f"**{report.get('talk_ratio', 'N/A')}**")
                st.caption(report.get('talk_ratio_assessment', ''))
                
                st.markdown("---")
                
                # Session Flow
                st.write("### 🎯 Session Flow Quality / جودة تدفق الجلسة")
                flow = report.get('session_flow', {})
                
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                
                with col1:
                    opening = flow.get('opening', 'N/A')
                    if 'Strong' in opening:
                        st.success(f"**📂 Opening**\n\n{opening}")
                    elif 'Weak' in opening:
                        st.error(f"**📂 Opening**\n\n{opening}")
                    else:
                        st.warning(f"**📂 Opening**\n\n{opening}")
                
                with col2:
                    exploration = flow.get('exploration', 'N/A')
                    if 'Strong' in exploration:
                        st.success(f"**🔍 Exploration**\n\n{exploration}")
                    elif 'Weak' in exploration:
                        st.error(f"**🔍 Exploration**\n\n{exploration}")
                    else:
                        st.warning(f"**🔍 Exploration**\n\n{exploration}")
                
                with col3:
                    deepening = flow.get('deepening', 'N/A')
                    if 'Strong' in deepening:
                        st.success(f"**💎 Deepening**\n\n{deepening}")
                    elif 'Weak' in deepening:
                        st.error(f"**💎 Deepening**\n\n{deepening}")
                    else:
                        st.warning(f"**💎 Deepening**\n\n{deepening}")
                
                with col4:
                    closing = flow.get('closing', 'N/A')
                    if 'Strong' in closing:
                        st.success(f"**🎯 Closing**\n\n{closing}")
                    elif 'Weak' in closing:
                        st.error(f"**🎯 Closing**\n\n{closing}")
                    else:
                        st.warning(f"**🎯 Closing**\n\n{closing}")
                
                st.markdown("---")
                
                # Strengths and Areas for Improvement
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("### ✅ Strengths / نقاط القوة")
                    strengths = report.get('strengths', [])
                    for i, strength in enumerate(strengths, 1):
                        st.success(f"**{i}.** {strength}")
                
                with col2:
                    st.write("### 💡 Areas for Improvement / مجالات التحسين")
                    improvements = report.get('areas_for_improvement', [])
                    for i, improvement in enumerate(improvements, 1):
                        st.warning(f"**{i}.** {improvement}")
                
                st.markdown("---")
                
                # Key Moments
                st.write("### ⭐ Key Moments / اللحظات الرئيسية")
                key_moments = report.get('key_moments', [])
                if key_moments:
                    for moment in key_moments:
                        with st.expander(f"**{moment.get('timestamp', '')}**: {moment.get('what_happened', '')}", expanded=False):
                            st.write(f"**Significance:** {moment.get('significance', 'N/A')}")
                else:
                    st.caption("No key moments identified")
                
                st.markdown("---")
                
                # Recommendations
                st.write("### 🎯 Actionable Recommendations / التوصيات العملية")
                recommendations = report.get('recommendations', [])
                for i, rec in enumerate(recommendations, 1):
                    st.info(f"**{i}.** {rec}")
            
            else:
                st.error(f"Error generating report: {report.get('error', 'Unknown error')}")
            
            st.markdown("---")
            
            # PDF Download Button
            col1, col2 = st.columns([1, 1])
            
            with col1:
                try:
                    from pdf_renderer import generate_session_pdf
                    pdf_bytes = generate_session_pdf(report, language=language)
                    
                    st.download_button(
                        label="📥 Download PDF Report / تحميل تقرير PDF",
                        data=pdf_bytes,
                        file_name=f"coaching_session_report_{report.get('session_duration', 'session').replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {str(e)}")
            
            with col2:
                if st.button("🔄 Start New Session", use_container_width=True):
                    st.session_state.full_session_active = False
                    st.session_state.final_session_report = None
                    st.session_state.session_messages = []
                    st.session_state.hidden_analyses = []
                    st.rerun()
        

    # MODE B: DIFFICULT CLIENT SIMULATOR
    elif mode_b_label in selected_mode:
        st.subheader("🎭 Difficult Client Simulator")
        st.write("Practice with challenging client personas!" if language == "English" else "تدرب مع شخصيات عملاء صعبة!")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            persona_options = {
                "resistant": "🛡️ Resistant (Defensive, doesn't want change)" if language == "English" else "🛡️ مقاوم (دفاعي، لا يريد التغيير)",
                "looping": "🔄 Looping (Repeats same story, stuck)" if language == "English" else "🔄 متكرر (يكرر نفس القصة)",
                "emotional": "😢 Emotional (Highly emotional, hard to partner)" if language == "English" else "😢 عاطفي (شديد العاطفة)",
                "analytical": "🤔 Analytical (Overthinking, analysis paralysis)" if language == "English" else "🤔 تحليلي (تفكير زائد)",
                "urgent": "⚡ Urgent (Wants quick fixes, impatient)" if language == "English" else "⚡ عجول (يريد حلول سريعة)"
            }
            
            selected_persona_label = st.selectbox(
                "Select Client Persona / اختر شخصية العميل",
                list(persona_options.values())
            )
            
            # Reverse lookup to get persona key
            st.session_state.client_persona = [k for k, v in persona_options.items() if v == selected_persona_label][0]
        
        with col2:
            topic_options = {
                "family": "👨‍👩‍👧‍👦 Family (Relationships, children, parents)" if language == "English" else "👨‍👩‍👧‍👦 العائلة (علاقات، أطفال، والدين)",
                "career": "💼 Career (Work, promotion, job change)" if language == "English" else "💼 المهنة (عمل، ترقية، تغيير وظيفة)",
                "relationships": "💑 Relationships (Partner, dating, marriage)" if language == "English" else "💑 العلاقات (شريك، مواعدة، زواج)",
                "finance": "💰 Finance (Money, savings, debt)" if language == "English" else "💰 المال (نقود، ادخار، ديون)",
                "life_goals": "🎯 Life Goals (Purpose, direction, dreams)" if language == "English" else "🎯 أهداف الحياة (هدف، اتجاه، أحلام)",
                "emotions": "😰 Stress/Emotions (Anxiety, fear, anger)" if language == "English" else "😰 التوتر/المشاعر (قلق، خوف، غضب)",
                "balance": "⚖️ Work-Life Balance (Burnout, priorities)" if language == "English" else "⚖️ التوازن (إرهاق، أولويات)",
                "growth": "🎓 Personal Growth (Skills, confidence, change)" if language == "English" else "🎓 النمو الشخصي (مهارات، ثقة، تغيير)"
            }
            
            selected_topic_label = st.selectbox(
                "Select Topic / اختر الموضوع",
                list(topic_options.values())
            )
            
            # Reverse lookup to get topic key
            if 'client_topic' not in st.session_state:
                st.session_state.client_topic = "career"
            st.session_state.client_topic = [k for k, v in topic_options.items() if v == selected_topic_label][0]
        
        col3, col4 = st.columns([2, 1])
        
        with col4:
            if st.button("🔄 Reset Conversation / إعادة تعيين المحادثة", use_container_width=True):
                st.session_state.conversation_history = []
                if 'coach_textarea_value' in st.session_state:
                    del st.session_state.coach_textarea_value
                if 'transcribed_text' in st.session_state:
                    del st.session_state.transcribed_text
                st.session_state.mentor_feedback = {}
                st.session_state.last_audio_hash = None
                st.session_state.audio_input_key += 1  # Force audio input to reset
                st.rerun()
        
        st.markdown("---")
        
        # Initialize conversation if empty
        if len(st.session_state.conversation_history) == 0 and api_key:
            from training_engine import TrainingEngine
            trainer = TrainingEngine(api_key, markers_data)
            with st.spinner("Client is thinking..." if language == "English" else "العميل يفكر..."):
                opening = trainer.simulate_difficult_client(
                    st.session_state.client_persona,
                    [],
                    st.session_state.get('client_topic', 'career'),
                    language=language
                )
                if 'error' not in opening:
                    st.session_state.conversation_history.append({
                        'role': 'Client',
                        'content': opening.get('client_response', 'Hello Coach.')
                    })
        
        # Display conversation
        for idx, msg in enumerate(st.session_state.conversation_history):
            role = msg.get('role', '')
            content = msg.get('content', '')
            
            if role == 'Client':
                with st.chat_message("user", avatar="🧑"):
                    st.write(f"**Client:** {content}")
            elif role == 'Coach':
                with st.chat_message("assistant", avatar="🎯"):
                    st.write(f"**You (Coach):** {content}")
        
        # Show mentor feedback AFTER the conversation (at the bottom)
        if st.session_state.conversation_history:
            # Find the last coach message
            last_coach_idx = None
            for idx in range(len(st.session_state.conversation_history) - 1, -1, -1):
                if st.session_state.conversation_history[idx].get('role') == 'Coach':
                    last_coach_idx = idx
                    break
            
            # Show mentor feedback if available
            if last_coach_idx is not None and last_coach_idx in st.session_state.mentor_feedback:
                st.markdown("---")
                st.write("### 💡 Mentor's Analysis / تحليل الموجه")
                
                feedback = st.session_state.mentor_feedback[last_coach_idx]
                
                # Score with color coding
                score = feedback.get('score', 0)
                col1, col2, col3 = st.columns([1, 2, 2])
                
                with col1:
                    if score >= 7:
                        st.success(f"### 🌟 {score}/10")
                    elif score >= 4:
                        st.warning(f"### ⚠️ {score}/10")
                    else:
                        st.error(f"### ❌ {score}/10")
                
                with col2:
                    rating = feedback.get('rating', 'N/A')
                    if rating == 'Strong':
                        st.success(f"**Rating:** {rating}")
                    elif rating == 'Acceptable':
                        st.warning(f"**Rating:** {rating}")
                    else:
                        st.error(f"**Rating:** {rating}")
                
                with col3:
                    markers = feedback.get('markers_demonstrated', [])
                    if markers:
                        st.info(f"**Markers:** {', '.join(markers)}")
                    else:
                        st.caption("No markers clearly demonstrated")
                
                # Feedback
                fb_text = feedback.get('feedback', '')
                if fb_text:
                    st.write("**📋 Feedback:**")
                    st.info(fb_text)
                
                # What could be better
                better = feedback.get('what_could_be_better', '')
                if better:
                    st.write("**💡 What Could Be Better:**")
                    st.warning(better)
                
                # Recommendation
                recommendation = feedback.get('recommendation', '')
                if recommendation:
                    st.write("**✨ Key Takeaway:**")
                    st.success(recommendation)
        
        st.markdown("---")
        
        # Voice-to-Text Recording Section
        st.write("### 🎤 Voice Input (Optional) / الإدخال الصوتي (اختياري)")
        
        audio_input = st.audio_input(
            "Record your coaching response / سجل ردك التدريبي",
            key=f"client_sim_audio_{st.session_state.audio_input_key}"
        )
        
        # Initialize transcribed_text in session state
        if 'transcribed_text' not in st.session_state:
            st.session_state.transcribed_text = ""
        
        if audio_input:
            audio_hash = hash(audio_input.getvalue())
            if audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = audio_hash
                try:
                    with st.spinner("Transcribing..." if language == "English" else "جاري النسخ..."):
                        from training_engine import TrainingEngine
                        trainer = TrainingEngine(api_key, markers_data)
                        transcript = trainer.transcribe_audio(audio_input, language=language)
                        
                        # Check if transcription failed
                        if "error" in transcript.lower() or "خطأ" in transcript:
                            st.error(transcript)
                            st.session_state.transcribed_text = ""
                        else:
                            st.session_state.transcribed_text = transcript
                            st.success("✅ Transcribed! Edit below if needed." if language == "English" else "✅ تم النسخ! عدل بالأسفل إذا لزم الأمر.")
                except Exception as e:
                    st.error(f"Transcription failed: {str(e)}" if language == "English" else f"فشل النسخ: {str(e)}")
                    st.session_state.transcribed_text = ""
        
        # Show transcribed text in editable area if available
        if st.session_state.get('transcribed_text', ''):
            st.write("**📝 Transcribed Text (Edit if needed) / النص المنسوخ (عدل إذا لزم الأمر):**")
            edited_transcript = st.text_area(
                "Transcribed text / النص المنسوخ",
                value=st.session_state.transcribed_text,
                height=100,
                key="transcript_editor",
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✅ Use this text / استخدم هذا النص", use_container_width=True, type="primary", key="use_text_btn"):
                    # Delete the key if exists, then store the text for next rerun
                    if 'coach_textarea_value' in st.session_state:
                        del st.session_state.coach_textarea_value
                    st.session_state['_pending_coach_text'] = edited_transcript
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear / مسح", use_container_width=True, key="clear_transcript_btn"):
                    if 'transcribed_text' in st.session_state:
                        del st.session_state.transcribed_text
                    if 'last_audio_hash' in st.session_state:
                        del st.session_state.last_audio_hash
                    st.rerun()
        
        st.markdown("---")
        
        # Initialize coach_textarea_value if not exists
        if 'coach_textarea_value' not in st.session_state:
            # Check if there's pending text from "Use this text" button
            if '_pending_coach_text' in st.session_state:
                st.session_state.coach_textarea_value = st.session_state._pending_coach_text
                del st.session_state._pending_coach_text
            else:
                st.session_state.coach_textarea_value = ""
        
        # Coach input (separate from voice)
        st.write("### ⌨️ Text Response / الرد النصي")
        coach_response = st.text_area(
            "Type your response OR use transcribed text above / اكتب ردك أو استخدم النص المنسوخ أعلاه",
            height=120,
            key="coach_textarea_value",
            placeholder="Type your coaching response here... / اكتب ردك التدريبي هنا..."
        )
        
        if st.button("📤 Send / إرسال", type="primary"):
            # Use the value from session_state
            coach_response_text = st.session_state.get('coach_textarea_value', '')
            
            if not coach_response_text.strip():
                st.warning("Please type your response" if language == "English" else "الرجاء كتابة ردك")
            elif not api_key:
                st.error("Please enter API Key" if language == "English" else "الرجاء إدخال API Key")
            else:
                from training_engine import TrainingEngine
                trainer = TrainingEngine(api_key, markers_data)
                
                with st.spinner("Processing..." if language == "English" else "جاري المعالجة..."):
                    # Add coach message
                    st.session_state.conversation_history.append({
                        'role': 'Coach',
                        'content': coach_response_text
                    })
                    
                    # Get mentor feedback
                    feedback = trainer.evaluate_coach_response(
                        st.session_state.conversation_history,
                        coach_response_text,
                        language=language
                    )
                    
                    # Store feedback for this message
                    coach_msg_idx = len(st.session_state.conversation_history) - 1
                    st.session_state.mentor_feedback[coach_msg_idx] = feedback
                    
                    # Get client response
                    client_response = trainer.simulate_difficult_client(
                        st.session_state.client_persona,
                        st.session_state.conversation_history,
                        st.session_state.get('client_topic', 'career'),
                        language=language
                    )
                    
                    if 'error' not in client_response:
                        st.session_state.conversation_history.append({
                            'role': 'Client',
                            'content': client_response.get('client_response', 'I see...')
                        })
                    
                    # Clear fields - delete keys instead of setting to empty
                    if 'coach_textarea_value' in st.session_state:
                        del st.session_state.coach_textarea_value
                    if 'transcribed_text' in st.session_state:
                        del st.session_state.transcribed_text
                    st.rerun()


# --- MY PROFILE ---
elif mode == t["mode_profile"]:
    st.header(t["mode_profile"])
    
    user_email = st.session_state.user_email
    user_id = st.session_state.user_id
    st.write(f"### 👤 {user_email}")
    st.write(f"📧 {user_email}")
    
    # Fetch History
    with st.spinner("Loading history..."):
        history = firebase_config.get_user_history(user_id)
    
    if not history:
        st.info("No training history found yet. Start a session to see your progress!")
    else:
        # 1. Progress Chart
        st.subheader("📈 Progress Tracking / تتبع التطور")
        
        # Prepare data for chart
        chart_data = []
        for session in history:
            if 'score' in session:
                chart_data.append({
                    'Date': session.get('created_at'),
                    'Score': session.get('score'),
                    'Type': session.get('session_type', 'Unknown')
                })
        
        if chart_data:
            df_chart = pd.DataFrame(chart_data)
            fig = px.line(df_chart, x='Date', y='Score', color='Type', markers=True, title="Performance Over Time")
            fig.update_layout(yaxis_range=[0, 10])
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # 2. History Table
        st.subheader("📜 Session History / سجل الجلسات")
        
        for session in history:
            with st.expander(f"{session.get('date', 'Unknown Date')} - {session.get('session_type', 'Session')} (Score: {session.get('score', 'N/A')})"):
                st.write(f"**Duration:** {session.get('duration', 'N/A')}")
                st.write(f"**Score:** {session.get('score', 'N/A')}/10")
                
                # Show report summary if available
                if 'report_json' in session:
                    report = session['report_json']
                    st.json(report)

# Footer
st.markdown("---")
st.caption(t["footer"])
