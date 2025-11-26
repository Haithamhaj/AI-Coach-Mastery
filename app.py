import streamlit as st
import json
import os
import tempfile
import plotly.express as px
import pandas as pd
from translations import translations
from marker_helpers import get_marker_recommendation, get_marker_explanation

from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Page Configuration (MUST BE FIRST)
st.set_page_config(
    page_title="AI Coach Mastery - PCC Level Training",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FIREBASE KEY SETUP (Cloud Deployment Fix) ---
# Create firebase_key.json from secrets if it doesn't exist
if not os.path.exists("firebase_key.json"):
    try:
        # Check if we're in cloud environment with secrets
        if hasattr(st, 'secrets') and "firebase_service_account" in st.secrets:
            print("☁️ Creating firebase_key.json from secrets...")
            key_dict = dict(st.secrets["firebase_service_account"])
            
            # Fix private_key formatting issues
            if "private_key" in key_dict:
                key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
                
            with open("firebase_key.json", "w") as f:
                json.dump(key_dict, f)
            print("✅ firebase_key.json created successfully!")
        else:
            print("⚠️ Running locally - firebase_key.json not found.")
    except Exception as e:
        print(f"⚠️ Error creating firebase_key.json: {e}")
        # Don't crash, continue anyway

# Load Custom CSS and Fonts
def load_custom_css():
    # Load Google Fonts
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    # Load Custom CSS
    try:
        with open('static/styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # CSS file not found, continue without custom styles
    
    # Load Streamlit Components CSS
    try:
        with open('static/streamlit_components.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # CSS file not found, continue without custom styles

# Apply custom CSS
load_custom_css()

# Sidebar Language Selector
st.sidebar.image("logo.jpg", width=200)
language = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"], key="language_selector")
t = translations[language]

# --- NAVIGATION SETUP (Must be early for sidebar placement) ---
# Check if user is admin
from admin_middleware import get_admin_middleware
admin = get_admin_middleware()
is_admin_user = admin.is_admin(st.session_state.user_email) if 'user_email' in st.session_state else False

# Import User Dashboard
from user_dashboard import show_user_dashboard

# Navigation State
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Sidebar Navigation Options
nav_options = {
    "Home": "🏠 Home" if language == "English" else "🏠 الرئيسية",
    "Training": t["mode_training"],
    "Exam": t["mode_exam"]
}

if is_admin_user:
    nav_options["Admin"] = "📊 Admin Dashboard" if language == "English" else "📊 لوحة تحكم الأدمن"

# Create mappings
label_to_key = {v: k for k, v in nav_options.items()}

# Determine current selection
current_label = nav_options.get(st.session_state.current_page, nav_options["Home"])
options_list = list(nav_options.values())

try:
    default_index = options_list.index(current_label)
except ValueError:
    default_index = 0

# Callback function for sidebar navigation
def update_page_from_sidebar():
    """Update current_page when user changes sidebar radio"""
    selected_label = st.session_state.nav_radio
    selected_key = label_to_key[selected_label]
    st.session_state.current_page = selected_key

# Render Sidebar Navigation with callback (AT THE TOP!)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Navigation")
st.sidebar.radio(
    "",
    options_list,
    index=default_index,
    key="nav_radio",
    on_change=update_page_from_sidebar,
    label_visibility="collapsed"
)
st.sidebar.markdown("---")

# DEBUG: Show current user status
if 'user_email' in st.session_state:
    st.sidebar.markdown("---")
    st.sidebar.caption("🔧 Debug Info")
    st.sidebar.caption(f"User: {st.session_state.user_email}")
    
    from admin_middleware import get_admin_middleware
    admin_mw = get_admin_middleware()
    is_admin_check = admin_mw.is_admin(st.session_state.user_email)
    st.sidebar.caption(f"Is Admin: {is_admin_check}")
    st.sidebar.caption(f"Current Page: {st.session_state.get('current_page', 'Not Set')}")
    
    if is_admin_check:
        st.sidebar.success("Admin Access Active")
    else:
        st.sidebar.warning("No Admin Access")
        


# --- AUTHENTICATION SYSTEM ---
import auth_handler
import firebase_config

# Initialize Cookie Manager
try:
    from streamlit_cookies_manager import EncryptedCookieManager
    
    cookies = EncryptedCookieManager(
        prefix="ai_coach_mastery_",
        password=os.getenv("COOKIE_PASSWORD", "default_secret_key_change_me")
    )
    
    if not cookies.ready():
        # Wait for cookies to be ready
        st.spinner("Loading session...")
        st.stop()
except Exception:
    st.stop()

# Initialize Firebase (for Firestore only)
if 'firebase_initialized' not in st.session_state:
    if firebase_config.initialize_firebase():
        st.session_state.firebase_initialized = True
    else:
        st.session_state.firebase_initialized = False

# Try to auto-login from cookie if not authenticated
if not auth_handler.is_authenticated():
    saved_session = auth_handler.load_from_cookie(cookies=cookies)
    if saved_session:
        auth_handler.save_session(saved_session)
        st.rerun()

# Check if user wants to view landing page or login
if 'show_landing' not in st.session_state:
    st.session_state.show_landing = True

# Landing Page / Login Toggle
if not auth_handler.is_authenticated():
    # Show Landing Page if not logged in
    if st.session_state.get('show_landing', True):
        # Import and show native Streamlit landing page
        from landing_page import show_landing_page
        
        # Normalize language code for the landing page
        lang_code = 'ar' if language == "العربية" else 'en'
        show_landing_page(language=lang_code)
        
        # Handle component values (Login/Start)
        # Check for query param action=start_login
        query_params = st.query_params
        if query_params.get("action") == "start_login":
            st.session_state.show_landing = False
            # Clear the query param so we don't get stuck in a loop if they reload
            st.query_params.clear()
            st.rerun()

        # Also keep the old component check just in case, though likely unused now
        component_value = st.session_state.get('landing_page_component')
        if component_value == 'start_login':
            st.session_state.show_landing = False
            st.rerun()
            
        st.stop()  # Stop execution after showing landing page
    else:
        # Show Login/Signup Page
        st.title("🔐 Login / تسجيل الدخول")
        
        # Back to landing page button
        if st.button("← Back to Home", key="back_to_landing"):
            st.session_state.show_landing = True
            st.rerun()
        
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
                                # Save to cookie if remember_me is checked
                                if remember_me:
                                    with st.spinner("Saving login info..."):
                                        auth_handler.save_to_cookie(result, remember_me=True, cookies=cookies)
                                        import time
                                        time.sleep(2)  # Give time for cookie to save
                                
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
            
            # Divider
            st.markdown("---")
            st.write("### Or sign in with:")
            
            # Google Sign-In using Firebase JS SDK
            import streamlit.components.v1 as components
            
            # Check if Google auth callback happened
            if 'google_auth_token' in st.session_state and st.session_state.google_auth_token:
                # Process the Google login
                google_session = {
                    "success": True,
                    "email": st.session_state.google_auth_email,
                    "localId": st.session_state.google_auth_uid,
                    "idToken": st.session_state.google_auth_token,
                    "refreshToken": "google_refresh_token"
                }
                auth_handler.save_session(google_session)
                
                # Also create user profile in Firestore if doesn't exist
                firebase_config.create_user(
                    st.session_state.google_auth_email,
                    "google_oauth_user",
                    st.session_state.google_auth_email.split('@')[0]
                )
                
                # Clear the temporary state
                del st.session_state.google_auth_token
                del st.session_state.google_auth_email
                del st.session_state.google_auth_uid
                
                st.rerun()
            
            # Firebase configuration from environment
            firebase_api_key = os.getenv("FIREBASE_API_KEY")
            firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")
            
            # Google Sign-In Button with Firebase JS SDK
            google_signin_html = f"""
            <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"></script>
            <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-auth-compat.js"></script>
            
            <style>
                .google-btn {{
                    background: rgba(15, 23, 42, 0.7);
                    backdrop-filter: blur(12px);
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    color: #ffffff;
                    cursor: pointer;
                    font-family: 'Inter', 'Roboto', arial, sans-serif;
                    font-size: 14px;
                    font-weight: 600;
                    height: 48px;
                    letter-spacing: 0.25px;
                    padding: 0 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    width: 100%;
                    max-width: 300px;
                    margin: 0 auto;
                    transition: all 0.3s ease;
                }}
                .google-btn:hover {{
                    border-color: rgba(6, 182, 212, 0.5);
                    transform: translateY(-2px);
                    box-shadow: 0 10px 40px rgba(6, 182, 212, 0.2);
                }}
                .google-btn:active {{
                    transform: translateY(0);
                }}
            </style>
            
            <button id="googleSignInBtn" class="google-btn">
                <svg width="18" height="18" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
                    <path fill="none" d="M0 0h48v48H0z"></path>
                </svg>
                Sign in with Google
            </button>
            
            <div id="status"></div>
            
            <script>
                const firebaseConfig = {{
                    apiKey: "{firebase_api_key}",
                    authDomain: "{firebase_project_id}.firebaseapp.com",
                    projectId: "{firebase_project_id}"
                }};
                
                // Initialize Firebase
                if (!firebase.apps.length) {{
                    firebase.initializeApp(firebaseConfig);
                }}
                
                const auth = firebase.auth();
                const provider = new firebase.auth.GoogleAuthProvider();
                provider.setCustomParameters({{
                    prompt: 'select_account'
                }});
                
                document.getElementById('googleSignInBtn').addEventListener('click', async () => {{
                    const statusDiv = document.getElementById('status');
                    statusDiv.textContent = 'Opening Google Sign-In...';
                    
                    try {{
                        const result = await auth.signInWithPopup(provider);
                        const user = result.user;
                        const token = await user.getIdToken();
                        
                        statusDiv.textContent = 'Success! Redirecting...';
                        
                        // Send data back to Streamlit via query parameters
                        const currentUrl = new URL(window.location.href);
                        currentUrl.searchParams.set('google_token', token);
                        currentUrl.searchParams.set('google_email', user.email);
                        currentUrl.searchParams.set('google_uid', user.uid);
                        
                        window.parent.location.href = currentUrl.toString();
                        
                    }} catch (error) {{
                        console.error('Error during sign in:', error);
                        statusDiv.textContent = 'Sign-in failed: ' + error.message;
                    }}
                }});
            </script>
            """
            
            components.html(google_signin_html, height=100)
            
            # Check for Google auth callback in URL parameters
            query_params = st.query_params
            if 'google_token' in query_params:
                st.session_state.google_auth_token = query_params['google_token']
                st.session_state.google_auth_email = query_params['google_email']
                st.session_state.google_auth_uid = query_params['google_uid']
                
                # Clear query parameters
                st.query_params.clear()
                st.rerun()
        
        
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
                                create_result = firebase_config.create_user(new_email, new_password, new_email.split('@')[0])
                                
                                if "error" in create_result:
                                    st.error(f"Account created but profile failed: {create_result['error']}" if language == "English" else f"تم إنشاء الحساب ولكن فشل الملف الشخصي: {create_result['error']}")
                                else:
                                    st.success("Account created successfully! Please login." if language == "English" else "تم إنشاء الحساب بنجاح! الرجاء تسجيل الدخول.")
                            else:
                                error_msg = result.get("error", "Unknown error")
                                if "EMAIL_EXISTS" in error_msg:
                                    st.error("Email already exists" if language == "English" else "البريد الإلكتروني مستخدم بالفعل")
                                elif "WEAK_PASSWORD" in error_msg:
                                    st.error("Password is too weak" if language == "English" else "كلمة المرور ضعيفة جداً")
                                elif "OPERATION_NOT_ALLOWED" in error_msg:
                                    st.error("Email/Password sign-in is disabled in Firebase Console" if language == "English" else "تسجيل الدخول بالبريد/كلمة المرور معطل في Firebase")
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
    auth_handler.clear_cookie()  # Clear saved cookie
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



# Set 'mode' variable for backward compatibility with existing code
# This maps the new page keys to the old mode strings expected by the rest of the app
if st.session_state.current_page == "Training":
    mode = t["mode_training"]
elif st.session_state.current_page == "Exam":
    mode = t["mode_exam"]
elif st.session_state.current_page == "Admin":
    mode = "📊  Admin Dashboard" if language == "English" else "📊 لوحة تحكم الأدمن"
elif st.session_state.current_page == "Arcade":
    mode = "Arcade"
else:
    mode = "Home"

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
    fig.update_traces(fill='toself', fillcolor='rgba(6, 182, 212, 0.2)', 
                     line=dict(color='#06b6d4', width=3))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(15, 23, 42, 0.5)',
            radialaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.1)',
                tickfont=dict(color='#94a3b8')
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.1)',
                tickfont=dict(color='#ffffff')
            )
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Tajawal, Inter, sans-serif'),
        title_font=dict(size=20, color='#06b6d4')
    )
    return fig

# Main Content
st.title(t["title"])

# --- TRAINING MODE ---
if mode == "Home":
    show_user_dashboard(st.session_state.user_email, is_admin_user, language)

elif mode == t["mode_training"]:
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
        if 'grow_result' not in st.session_state:
            st.session_state.grow_result = None
            
        # Analyze Button
        if st.button(t["analyze_btn"]):
            if not api_key:
                st.error(t["enter_api_key"])
            else:
                from analysis_engine import AnalysisEngine
                # Create analysis engine with user tracking
                user_email = st.session_state.get('user_email', 'anonymous')
                engine = AnalysisEngine(api_key, markers_data, user_id=user_email)
                
                # Stage 1: Ethics Check = None
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
                        
                        # 3. GROW Model Analysis
                        with st.spinner("Analyzing Session Flow (GROW Model)..." if language == "English" else "جاري تحليل تدفق الجلسة (نموذج GROW)..."):
                            st.session_state.grow_result = engine.analyze_grow_model(content_to_analyze, is_audio=is_audio, language=language)
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
                        
                        # --- PCC PERFORMANCE AUDIT ---
                        st.markdown("## 🎯 PCC Performance Audit / تدقيق أداء PCC")
                        
                        # 1. Top Metrics Row (4 Columns)
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            markers_observed = analysis_result.get('markers_observed', 0)
                            compliance_pct = analysis_result.get('compliance_percentage', 0)
                            pcc_result = analysis_result.get('overall_pcc_result', 'Fail')
                            result_icon = "✅" if pcc_result == "Pass" else "❌"
                            st.metric("📊 Marker Compliance / الالتزام بالعلامات", f"{markers_observed}/37 ({compliance_pct:.0f}%)")
                            st.caption(f"{result_icon} {pcc_result}")
                        
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
                        
                        # Validation Warning (if markers are missing)
                        validation = analysis_result.get('validation_warning', {})
                        if validation.get('status') == 'INCOMPLETE':
                            st.warning(f"⚠️ **Validation Warning:** {validation.get('message', 'Some markers missing')}")
                            st.caption("The AI did not evaluate all 37 markers. Results may be incomplete.")
                        elif validation.get('status') == 'COMPLETE':
                            st.success("✅ All 37 markers evaluated")
                        
                        st.markdown("---")

                        # --- GROW MODEL ANALYSIS ---
                        if st.session_state.grow_result and "error" not in st.session_state.grow_result:
                            grow_data = st.session_state.grow_result
                            st.subheader("🌱 GROW Model Analysis / تحليل نموذج GROW")
                            
                            # Prepare data for Pie Chart
                            phases = grow_data.get('phases', {})
                            if phases:
                                pie_data = []
                                colors = {'Goal': '#FF4500', 'Reality': '#FFA500', 'Options': '#32CD32', 'Will': '#1E90FF'}
                                
                                for phase_name, phase_info in phases.items():
                                    pie_data.append({
                                        'Phase': phase_name,
                                        'Percentage': phase_info.get('percentage', 0),
                                        'Assessment': phase_info.get('assessment', '')
                                    })
                                
                                df_grow = pd.DataFrame(pie_data)
                                
                                col_grow_1, col_grow_2 = st.columns([1, 2])
                                
                                with col_grow_1:
                                    fig_pie = px.pie(df_grow, values='Percentage', names='Phase', 
                                                    title='Session Time Distribution' if language == "English" else 'توزيع وقت الجلسة',
                                                    color='Phase', color_discrete_map=colors, hole=0.4)
                                    fig_pie.update_layout(
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        font=dict(color='#ffffff', family='Tajawal, Inter, sans-serif'),
                                        showlegend=False
                                    )
                                    st.plotly_chart(fig_pie, use_container_width=True)
                                
                                with col_grow_2:
                                    st.write("### 📝 Phase Assessment / تقييم المراحل")
                                    for item in pie_data:
                                        with st.expander(f"**{item['Phase']} ({item['Percentage']}%)**", expanded=True):
                                            st.write(item['Assessment'])
                                    
                                    if 'overall_feedback' in grow_data:
                                        st.info(f"**💡 Overall Feedback:** {grow_data['overall_feedback']}")
                            
                            st.markdown("---")

                        # 2. 8 Competencies Overview (PCC Hierarchy)
                        st.subheader("📋 8 Core Competencies / الكفاءات الثمانية الأساسية")
                        
                        competencies_dict = analysis_result.get('competencies', {})
                        
                        if competencies_dict:
                            # Define competency order
                            comp_order = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
                            
                            for comp_id in comp_order:
                                if comp_id not in competencies_dict:
                                    continue
                                    
                                comp_data = competencies_dict[comp_id]
                                comp_name = comp_data.get('name', comp_id)
                                
                                # Count markers for this competency
                                markers_list = comp_data.get('markers', [])
                                if markers_list:
                                    observed = sum(1 for m in markers_list if m.get('status') == 'Observed')
                                    total = len(markers_list)
                                    comp_status = f"{observed}/{total} Markers"
                                    status_icon = "✅" if observed >= (total * 0.7) else "⚠️" if observed >= (total * 0.5) else "❌"
                                else:
                                    # For C1 and C2 (no individual markers)
                                    comp_status = comp_data.get('status', 'N/A')
                                    status_icon = "✅" if comp_status == "Pass" else "❌"
                                
                                with st.expander(f"{status_icon} **{comp_id}: {comp_name}** - {comp_status}", expanded=False):
                                    # Show feedback for C1 and C2
                                    if comp_id in ['C1', 'C2']:
                                        feedback = comp_data.get('feedback', 'No feedback available')
                                        st.info(feedback)
                                        
                                        if comp_id == 'C2':
                                            st.caption("**Note:** C2 is assessed through cross-cutting markers: 4.1, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 6.1, 6.5, 7.1, 7.5")
                                    
                                    # Show markers for C3-C8
                                    if markers_list:
                                        for marker in markers_list:
                                            marker_id = marker.get('id', '')
                                            behavior = marker.get('behavior', marker.get('text', ''))
                                            status = marker.get('status', 'Not Observed')
                                            evidence = marker.get('evidence', 'No evidence found')
                                            feedback = marker.get('feedback', marker.get('auditor_note', ''))
                                            
                                            # Create columns for better layout
                                            col1, col2 = st.columns([3, 1])
                                            
                                            with col1:
                                                if status == 'Observed':
                                                    st.success(f"**✅ Marker {marker_id}**: {behavior}")
                                                else:
                                                    st.error(f"**❌ Marker {marker_id}**: {behavior}")
                                            
                                            with col2:
                                                # Badge for competency category
                                                st.markdown(f"<div style='text-align: right; padding: 5px;'><span style='background: rgba(6, 182, 212, 0.1); color: #06b6d4; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; border: 1px solid rgba(6, 182, 212, 0.3);'>{comp_id}</span></div>", unsafe_allow_html=True)
                                            
                                            # Evidence section
                                            if evidence and evidence != 'No evidence found':
                                                st.markdown("**📝 Evidence:**")
                                                st.info(evidence)
                                            
                                            # Assessor feedback
                                            if feedback:
                                                st.markdown("**🎯 Assessor Notes:**")
                                                st.caption(feedback)
                                            
                                            # If marker NOT observed, show practical recommendations
                                            if status != 'Observed':
                                                with st.expander("💡 How to Improve This Marker", expanded=False):
                                                    # Get recommendations based on marker ID
                                                    recommendation = get_marker_recommendation(marker_id, language)
                                                    st.markdown(recommendation)
                                            
                                            # Show marker explanation
                                            with st.expander(f"ℹ️ What is Marker {marker_id}?", expanded=False):
                                                marker_explanation = get_marker_explanation(marker_id, comp_id, language)
                                                st.markdown(marker_explanation)
                                            
                                            st.markdown("---")
                        
                        st.markdown("---")

                        # 3. PDF Generation using ReportLab
                        from pdf_renderer import generate_mcc_pdf
                        
                        if st.button("📄 Download PCC Audit Report / تحميل تقرير التدقيق"):
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
                            if firebase_config.save_session(st.session_state.user_id, session_data):
                                st.success("✅ Session saved to your profile!" if language == "English" else "✅ تم حفظ الجلسة في ملفك الشخصي!")
                        else:
                            st.warning("⚠️ Login to save your progress" if language == "English" else "⚠️ سجل دخول لحفظ تقدمك")
            
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
                
                # Real-time GROW Assistant Tip
                grow_tips = {
                    "opening": "💡 **Goal Phase:** Establish trust and agree on the session goal.",
                    "exploration": "💡 **Reality Phase:** Explore the current situation. Ask 'What is happening now?'",
                    "deepening": "💡 **Options Phase:** Brainstorm possibilities. Ask 'What could you do?'",
                    "closing": "💡 **Will Phase:** Commit to action. Ask 'What will you do?'"
                }
                current_tip = grow_tips.get(st.session_state.session_phase, "")
                if current_tip:
                    st.caption(current_tip)
            
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
                
                # GROW Question Quality Analysis
                if 'grow_analysis' in report:
                    st.write("### 🌱 GROW Question Quality / جودة أسئلة نموذج GROW")
                    grow = report.get('grow_analysis', {})
                    
                    g_col1, g_col2, g_col3, g_col4 = st.columns(4)
                    
                    phases = [
                        ("Goal", "goal", "🎯"),
                        ("Reality", "reality", "🔍"),
                        ("Options", "options", "💡"),
                        ("Will", "will", "⚡")
                    ]
                    
                    # Display Scores
                    for i, (name, key, icon) in enumerate(phases):
                        data = grow.get(key, {})
                        score = data.get('score', 0)
                        with [g_col1, g_col2, g_col3, g_col4][i]:
                            st.metric(f"{icon} {name}", f"{score}/10")
                    
                    # Display Details
                    for name, key, icon in phases:
                        data = grow.get(key, {})
                        with st.expander(f"**{icon} {name} Phase Analysis**", expanded=False):
                            st.write(f"**Feedback:** {data.get('feedback', 'No feedback')}")
                            if data.get('key_questions'):
                                st.markdown("**Key Questions Asked:**")
                                for q in data.get('key_questions', []):
                                    st.caption(f"• {q}")

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
        
        col3, col4, col5 = st.columns([2, 1, 1])
        
        with col4:
            if st.button("🔄 Reset / إعادة تعيين", use_container_width=True):
                # Save session before reset if there's conversation history
                if auth_handler.is_authenticated() and len(st.session_state.conversation_history) > 0:
                    import datetime
                    session_data = {
                        'user_id': st.session_state.user_id,
                        'session_type': 'Difficult Client Simulator',
                        'score': len(st.session_state.conversation_history),  # Number of exchanges
                        'duration': "N/A",
                        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'report_json': {
                            'persona': st.session_state.client_persona,
                            'topic': st.session_state.client_topic,
                            'exchanges': len(st.session_state.conversation_history),
                            'conversation': st.session_state.conversation_history
                        }
                    }
                    firebase_config.save_session(st.session_state.user_id, session_data)
                
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
                
                # New Indicators Row
                i_col1, i_col2 = st.columns(2)
                with i_col1:
                    comp = feedback.get('primary_competency', 'N/A')
                    st.markdown(f"<div style='background-color:rgba(59, 130, 246, 0.1); color:#3b82f6; padding:8px; border-radius:5px; border:1px solid rgba(59, 130, 246, 0.3); text-align:center;'><strong>🏆 {comp}</strong></div>", unsafe_allow_html=True)
                with i_col2:
                    grow = feedback.get('grow_phase', 'N/A')
                    st.markdown(f"<div style='background-color:rgba(16, 185, 129, 0.1); color:#10b981; padding:8px; border-radius:5px; border:1px solid rgba(16, 185, 129, 0.3); text-align:center;'><strong>🌱 Phase: {grow}</strong></div>", unsafe_allow_html=True)
                
                st.write("") # Spacing
                
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

# --- ARCADE (GAME MODE) ---
elif mode == "Arcade":
    import arcade_game
    arcade_game.show(api_key, markers_data, language)

# Admin Dashboard Mode
elif ("Admin Dashboard" in mode or "لوحة تحكم" in mode):
    from admin_dashboard import show_admin_dashboard
    show_admin_dashboard()

# Footer
st.markdown("---")
st.caption(t["footer"])
