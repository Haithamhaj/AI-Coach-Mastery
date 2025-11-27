import streamlit as st
import pandas as pd
import plotly.express as px

def show_user_dashboard(user_email, is_admin=False, language="English"):
    """
    Displays the main User Dashboard with navigation cards and summary stats.
    """
    
    # Translations
    t = {
        "English": {
            "welcome": "Welcome back,",
            "dashboard": "Dashboard",
            "stats_title": "Your Progress",
            "sessions": "Total Sessions",
            "avg_score": "Avg. Score",
            "hours": "Training Hours",
            "start_training": "Start Training",
            "start_exam": "Start Exam",
            "view_profile": "View Profile",
            "admin_panel": "Admin Panel",
            "training_desc": "Practice with individual PCC markers and get instant AI feedback.",
            "exam_desc": "Full coaching session simulation with comprehensive evaluation.",
            "profile_desc": "Track your progress, history, and manage your account.",
            "admin_desc": "Manage users, view analytics, and system settings.",
            "gym_title": "Session Analysis Lab",
            "exam_title": "Training Lab",
            "profile_title": "My Coach Profile",
            "admin_title": "Admin Dashboard",
            "arcade_title": "Speed Skills Challenge",
            "arcade_title": "Speed Skills Challenge",
            "arcade_desc": "Play 'Spot-It Pro' to master competencies and markers in a fun way.",
            "learning_title": "Learning Hub",
            "learning_desc": "Master ICF Competencies, Markers, and GROW Model with AI Tutor.",
            "start_learning": "Go to Hub"
        },
        "العربية": {
            "welcome": "مرحباً بعودتك،",
            "dashboard": "لوحة التحكم",
            "stats_title": "تقدمك",
            "sessions": "عدد الجلسات",
            "avg_score": "متوسط الأداء",
            "hours": "ساعات التدريب",
            "start_training": "ابدأ التحليل",
            "start_exam": "ابدأ التدريب",
            "view_profile": "ملفي الشخصي",
            "admin_panel": "لوحة الإدارة",
            "training_desc": "ارفع مقطعًا من جلسة كوتشينج لتحليل المؤشرات والحصول على تغذية راجعة فورية.",
            "exam_desc": "اختر أحد تحديات المختبر لتطوير مهاراتك في إعادة الصياغة، التعامل مع العميل الصعب، أو قيادة جلسة كوتشينج كاملة.",
            "profile_desc": "تتبع تقدمك، سجلك، وإدارة حسابك.",
            "admin_desc": "إدارة المستخدمين، الإحصائيات، وإعدادات النظام.",
            "gym_title": "مختبر تحليل الجلسة",
            "exam_title": "مختبر التدريب",
            "profile_title": "ملفي ككوتش",
            "admin_title": "لوحة المشرف",
            "arcade_title": "تحدّي المهارات السريعة",
            "arcade_title": "تحدّي المهارات السريعة",
            "arcade_desc": "اختبر سرعة التقاطك لمؤشرات الكوتشينج من خلال تحدّي المهارات السريعة.",
            "learning_title": "مركز المعرفة",
            "learning_desc": "أتقن جدارات ICF والمؤشرات ونموذج GROW مع المعلم الذكي.",
            "start_learning": "اذهب للمركز"
        }
    }
    
    txt = t[language]
    
    # --- Header Section ---
    st.markdown(f"""
    <div style="padding: 20px; background-color: #1E1E1E; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="margin:0; color: #FFFFFF;">{txt['welcome']} {user_email.split('@')[0]} 👋</h1>
        <p style="color: #B0B0B0; margin-top: 5px;">{txt['dashboard']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Stats Row (Placeholder for now - can be connected to real data later) ---
    # In a real scenario, you would fetch these from Firestore
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label=txt['sessions'], value="0", delta=None)
    with col2:
        st.metric(label=txt['avg_score'], value="0%", delta=None)
    with col3:
        st.metric(label=txt['hours'], value="0h", delta=None)
        
    st.markdown("---")
    
    # --- Navigation Cards ---
    
    # Custom CSS for cards
    st.markdown("""
    <style>
    .nav-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #464B5C;
        height: 100%;
        transition: transform 0.2s;
    }
    .nav-card:hover {
        transform: translateY(-5px);
        border-color: #FF4B4B;
    }
    .card-title {
        color: #FFFFFF;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .card-desc {
        color: #B0B0B0;
        font-size: 0.9rem;
        margin-bottom: 20px;
        height: 60px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Grid Layout
    c1, c2 = st.columns(2)
    
    # Card 1: Learning Hub (NEW - First Position)
    with c1:
        with st.container():
            st.markdown(f"""
            <div class="nav-card">
                <div class="card-title">📚 {txt['learning_title']}</div>
                <div class="card-desc">{txt['learning_desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(txt['start_learning'], key="btn_nav_learning", use_container_width=True):
                st.session_state.current_page = "Learning Hub"
                st.rerun()

    # Card 2: Training
    with c2:
        with st.container():
            st.markdown(f"""
            <div class="nav-card">
                <div class="card-title">🏋️‍♂️ {txt['gym_title']}</div>
                <div class="card-desc">{txt['training_desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(txt['start_training'], key="btn_nav_training", use_container_width=True):
                st.session_state.current_page = "Training"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    # Card 3: Exam
    with c3:
        with st.container():
            st.markdown(f"""
            <div class="nav-card">
                <div class="card-title">📝 {txt['exam_title']}</div>
                <div class="card-desc">{txt['exam_desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(txt['start_exam'], key="btn_nav_exam", use_container_width=True):
                st.session_state.current_page = "Exam"
                st.rerun()

    # Card 4: Arcade
    with c4:
        with st.container():
            st.markdown(f"""
            <div class="nav-card">
                <div class="card-title">🧩 {txt.get('arcade_title', 'The Arcade')}</div>
                <div class="card-desc">{txt.get('arcade_desc', 'Play Spot-It Pro')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🎮 Play Now / العب الآن", key="btn_nav_arcade", use_container_width=True):
                st.session_state.current_page = "Arcade"
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    
    with c5:
        with st.container():
            st.markdown(f"""
            <div class="nav-card">
                <div class="card-title">👤 {txt['profile_title']}</div>
                <div class="card-desc">{txt['profile_desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(txt['view_profile'], key="btn_nav_profile", use_container_width=True):
                st.session_state.current_page = "Profile"
                st.rerun()
                
    # Conditional third card: Admin Dashboard
    if is_admin:
        st.markdown("<br>", unsafe_allow_html=True)
        c3, c4 = st.columns([1, 1])
        with c3:
            with st.container():
                st.markdown(f"""
                <div class="nav-card">
                    <div class="card-title">📊 {txt['admin_title']}</div>
                    <div class="card-desc">{txt['admin_desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(txt['admin_panel'], key="btn_nav_admin", use_container_width=True):
                    st.session_state.current_page = "Admin"
                    st.rerun()
