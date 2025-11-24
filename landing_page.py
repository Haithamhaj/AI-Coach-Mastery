"""
Landing Page for AI Coach Mastery
"""
import streamlit as st

def show_landing_page(language="English"):
    """Display the landing page"""
    
    # Determine text direction
    is_rtl = language == "العربية"
    direction = "rtl" if is_rtl else "ltr"
    
    # Translations
    t = {
        "English": {
            "title": "AI Coach Mastery",
            "subtitle": "Your Gateway to Coaching Excellence",
            "description": "An intelligent platform that works as an evaluator and personal mentor, helping you master ICF competencies and all 37 PCC markers through accurate analysis and realistic simulation.",
            "stat1_num": "37",
            "stat1_label": "PCC Markers",
            "stat2_num": "8",
            "stat2_label": "ICF Competencies",
            "stat3_num": "95%",
            "stat3_label": "Analysis Accuracy",
            "features_title": "✨ Key Features",
            "feature1_title": "📊 Deep Session Analysis",
            "feature1_desc": "Upload your audio or text files and get instant marker audits, talk ratio analysis, and performance gap detection.",
            "feature2_title": "🎭 Client Simulation (AI Persona)",
            "feature2_desc": "Practice in a safe environment with virtual clients in challenging patterns (resistant, emotional, analytical) and get real-time guidance.",
            "feature3_title": "🏆 Objective PCC Evaluation",
            "feature3_desc": "Unbiased and instant feedback based on 37 ICF behavioral markers, accelerating your journey to international certification.",
            "how_title": "🚀 How It Works",
            "step1_title": "Upload Your Session",
            "step1_desc": "Upload audio or text file",
            "step2_title": "Smart Analysis",
            "step2_desc": "AI analyzes all markers",
            "step3_title": "Detailed Report",
            "step3_desc": "Strengths and gaps",
            "step4_title": "Practice & Improve",
            "step4_desc": "Continuous simulation",
            "cta_title": "Ready to Become a Professional Coach?",
            "cta_subtitle": "Start your journey to excellence with AI Coach Mastery - Your smart platform for mastering ICF standards",
            "cta_button": "🚀 Start Now",
            "footer_copyright": "© 2024 AI Coach Mastery. All Rights Reserved",
            "footer_features": "✓ Accurate Session Analysis • ✓ Realistic Simulation • ✓ Instant Evaluation"
        },
        "العربية": {
            "title": "AI Coach Mastery",
            "subtitle": "بوابتك لاحتراف الكوتشينج",
            "description": "منصة ذكية تعمل كمقيم وموجه شخصي (Mentor)، تساعدك على إتقان جدارات ICF وعلامات PCC الـ 37 من خلال التحليل الدقيق والمحاكاة الواقعية.",
            "stat1_num": "37",
            "stat1_label": "علامة PCC",
            "stat2_num": "8",
            "stat2_label": "جدارات ICF",
            "stat3_num": "95%",
            "stat3_label": "دقة التحليل",
            "features_title": "✨ المميزات الرئيسية",
            "feature1_title": "📊 تحليل الجلسات المعمق",
            "feature1_desc": "ارفع ملفاتك الصوتية أو النصية واحصل على تدقيق فوري للعلامات، تحليل نسب التحدث، وكشف الفجوات في الأداء.",
            "feature2_title": "🎭 محاكاة العملاء (AI Persona)",
            "feature2_desc": "تدرب في بيئة آمنة مع عملاء افتراضيين بأنماط صعبة (المقاوم، العاطفي، كثير التفكير) واحصل على توجيه لحظي.",
            "feature3_title": "🏆 تقييم PCC الموضوعي",
            "feature3_desc": "تغذية راجعة حيادية وفورية تستند إلى 37 علامة سلوكية لـ ICF، مما يسرع رحلتك نحو الاعتماد الدولي.",
            "how_title": "🚀 كيف يعمل",
            "step1_title": "ارفع جلستك",
            "step1_desc": "حمّل ملف صوتي أو نصي",
            "step2_title": "تحليل ذكي",
            "step2_desc": "AI يحلل كل العلامات",
            "step3_title": "تقرير مفصل",
            "step3_desc": "نقاط القوة والفجوات",
            "step4_title": "تدرب وحسّن",
            "step4_desc": "محاكاة مستمرة",
            "cta_title": "هل أنت مستعد لتصبح كوتش محترف؟",
            "cta_subtitle": "ابدأ رحلتك نحو التميز مع AI Coach Mastery - منصتك الذكية لإتقان معايير ICF",
            "cta_button": "🚀 ابدأ الآن",
            "footer_copyright": "© 2024 AI Coach Mastery. جميع الحقوق محفوظة",
            "footer_features": "✓ تحليل دقيق للجلسات • ✓ محاكاة واقعية • ✓ تقييم فوري"
        }
    }
    
    txt = t[language]

    # --- 1. Page Configuration ---
    st.set_page_config(
        page_title="AI Coach Mastery",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # --- 2. Custom CSS for Styling ---
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {{
            margin: 0;
            padding: 0;
            background-color: #0f172a; /* Dark blue-gray background */
            color: #e2e8f0; /* Light gray text */
            font-family: 'Cairo', sans-serif;
            direction: {direction};
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: #ffffff; /* White headings */
            font-weight: 900;
        }}
        
        .stButton > button {{
            background-color: #3b82f6; /* Blue button */
            color: white;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-size: 1.1rem;
            font-weight: 700;
            border: none;
            transition: background-color 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .stButton > button:hover {{
            background-color: #2563eb; /* Darker blue on hover */
            cursor: pointer;
        }}
        
        /* Custom styling for columns to ensure consistent height */
        .st-emotion-cache-h4xjwh {{
            gap: 2rem;
        }}
        
        /* Hero Section */
        .hero-section {{
            text-align: center;
            padding: 6rem 2rem;
            background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); /* Gradient background */
            border-bottom-left-radius: 30px;
            border-bottom-right-radius: 30px;
            margin-bottom: 3rem;
            direction: {direction};
        }}
        .hero-title {{
            font-size: 4rem;
            font-weight: 900;
            margin-bottom: 1rem;
            line-height: 1.2;
            color: #ffffff;
        }}
        .hero-subtitle {{
            font-size: 1.8rem;
            color: #93c5fd; /* Light blue */
            margin-bottom: 2rem;
            font-weight: 700;
        }}
        .hero-description {{
            font-size: 1.2rem;
            color: #cbd5e1; /* Gray text */
            max-width: 800px;
            margin: 0 auto 3rem auto;
            line-height: 1.7;
        }}
        
        /* Stats Section */
        .stats-container {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-top: 3rem;
            flex-wrap: wrap;
            direction: {direction};
        }}
        .stat-item {{
            text-align: center;
            background: rgba(30, 58, 138, 0.5); /* Darker blue with transparency */
            padding: 1.5rem 2rem;
            border-radius: 12px;
            border: 1px solid rgba(59, 130, 246, 0.3);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            min-width: 180px;
        }}
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 900;
            color: #38bdf8; /* Sky blue */
            margin-bottom: 0.5rem;
        }}
        .stat-label {{
            font-size: 1rem;
            color: #94a3b8; /* Light gray */
            font-weight: 700;
        }}
        
        /* General Section Styling */
        .section-title {{
            text-align: center;
            font-size: 2.5rem;
            font-weight: 900;
            margin: 3rem 0 2rem 0;
            color: #ffffff;
        }}
        
        /* Feature Cards */
        .feature-card {{
            padding: 1.5rem;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            height: 100%;
        }}
        .feature-title {{
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }}
        .feature-desc {{
            color: #94a3b8;
            line-height: 1.6;
        }}
        
        /* How It Works Steps */
        .step-card {{
            text-align: center;
            padding: 2rem 1rem;
            border-radius: 16px;
            border: 1px solid;
            background: rgba(0,0,0,0.1);
        }}
        .step-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        .step-title {{
            color: #ffffff;
            margin-bottom: 0.5rem;
        }}
        .step-desc {{
            color: #94a3b8;
            font-size: 0.9rem;
        }}
        
        /* CTA Section */
        }
        </style>
    """, unsafe_allow_html=True)

    try:
        # Read the original HTML file
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # --- 1. Embed Images as Base64 ---
        # Logo
        logo_b64 = get_image_base64("logo.jpg")
        if logo_b64:
            # Replace logo src specifically
            html_content = html_content.replace('src="logo.jpg"', f'src="data:image/jpeg;base64,{logo_b64}"')
            
        # Feature Images
        for img_name in ["feature1.png", "feature2.png", "feature3.png"]:
            img_b64 = get_image_base64(img_name)
            if img_b64:
                html_content = html_content.replace(f'src="{img_name}"', f'src="data:image/png;base64,{img_b64}"')

        # --- 2. Fix Layout (Full Width Navbar) ---
        html_content = html_content.replace('max-w-7xl mx-auto', 'w-full px-6 md:px-12 mx-auto')

        # --- 3. Enforce Language & Interaction ---
        # Determine target language code for JS
        target_lang = 'ar' if language == "العربية" else 'en'
        
        # NOTE: Double braces {{ }} used for JS code inside f-string
        script_to_inject = f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                // 1. Handle Language
                const targetLang = '{target_lang}';
                const htmlRoot = document.getElementById('html-root');
                
                // Function to set language
                function setLanguage(lang) {{
                    if (!htmlRoot) return;
                    
                    if (lang === 'ar') {{
                        htmlRoot.setAttribute('lang', 'ar');
                        htmlRoot.setAttribute('dir', 'rtl');
                        document.body.style.direction = 'rtl';
                        // Trigger any existing translation logic if available
                        if (typeof updateContent === 'function') updateContent('ar');
                    }} else {{
                        htmlRoot.setAttribute('lang', 'en');
                        htmlRoot.setAttribute('dir', 'ltr');
                        document.body.style.direction = 'ltr';
                        if (typeof updateContent === 'function') updateContent('en');
                    }}
                }}
                
                // Set initial language
                setLanguage(targetLang);
                
                // 2. Handle Buttons (Start/Login)
                const buttons = document.querySelectorAll('a[href="#login"], button, .cta-button');
                buttons.forEach(btn => {{
                    btn.addEventListener('click', function(e) {{
                        const text = btn.innerText.toLowerCase();
                        if (text.includes('ابدأ') || text.includes('start') || text.includes('login') || btn.getAttribute('href') === '#login') {{
                            e.preventDefault();
                            window.parent.postMessage({{type: 'streamlit:set_component_value', value: 'start_login'}}, '*');
                        }}
                    }});
                }});
                
                // 3. Handle Language Toggle Button Click
                const langBtn = document.getElementById('langToggle');
                if (langBtn) {{
                    langBtn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        // Toggle local state
                        const currentDir = htmlRoot.getAttribute('dir');
                        const newLang = currentDir === 'rtl' ? 'en' : 'ar';
                        setLanguage(newLang);
                    }});
                }}
            }});
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features Section
    st.markdown(f"""
    <h2 style="text-align: center; font-size: 2.5rem; font-weight: 900; margin: 3rem 0 2rem 0; color: #ffffff; direction: {direction};">
        {txt['features_title']}
    </h2>
    """, unsafe_allow_html=True)
    
    feat1, feat2, feat3 = st.columns(3)
    
    with feat1:
        try:
            st.image("feature1.png", use_container_width=True)
        except:
            pass
        st.markdown(f"""
        <div style="padding: 1.5rem; background: rgba(15, 23, 42, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); height: 100%; direction: {direction};">
            <h3 style="color: #06b6d4; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">
                {txt['feature1_title']}
            </h3>
            <p style="color: #94a3b8; line-height: 1.6;">
                {txt['feature1_desc']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat2:
        try:
            st.image("feature2.png", use_container_width=True)
        except:
            pass
        st.markdown(f"""
        <div style="padding: 1.5rem; background: rgba(15, 23, 42, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); height: 100%; direction: {direction};">
            <h3 style="color: #a855f7; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">
                {txt['feature2_title']}
            </h3>
            <p style="color: #94a3b8; line-height: 1.6;">
                {txt['feature2_desc']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat3:
        try:
            st.image("feature3.png", use_container_width=True)
        except:
            pass
        st.markdown(f"""
        <div style="padding: 1.5rem; background: rgba(15, 23, 42, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); height: 100%; direction: {direction};">
            <h3 style="color: #f59e0b; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">
                {txt['feature3_title']}
            </h3>
            <p style="color: #94a3b8; line-height: 1.6;">
                {txt['feature3_desc']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # How It Works
    st.markdown(f"""
    <h2 style="text-align: center; font-size: 2.5rem; font-weight: 900; margin: 3rem 0 2rem 0; color: #ffffff; direction: {direction};">
        {txt['how_title']}
    </h2>
    """, unsafe_allow_html=True)
    
    step1, step2, step3, step4 = st.columns(4)
    
    with step1:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 1rem; background: rgba(6, 182, 212, 0.1); border-radius: 16px; border: 1px solid rgba(6, 182, 212, 0.3); direction: {direction};">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📤</div>
            <h4 style="color: #ffffff; margin-bottom: 0.5rem;">{txt['step1_title']}</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">{txt['step1_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 1rem; background: rgba(139, 92, 246, 0.1); border-radius: 16px; border: 1px solid rgba(139, 92, 246, 0.3); direction: {direction};">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
            <h4 style="color: #ffffff; margin-bottom: 0.5rem;">{txt['step2_title']}</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">{txt['step2_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step3:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 1rem; background: rgba(245, 158, 11, 0.1); border-radius: 16px; border: 1px solid rgba(245, 158, 11, 0.3); direction: {direction};">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
            <h4 style="color: #ffffff; margin-bottom: 0.5rem;">{txt['step3_title']}</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">{txt['step3_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step4:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 1rem; background: rgba(34, 197, 94, 0.1); border-radius: 16px; border: 1px solid rgba(34, 197, 94, 0.3); direction: {direction};">
            <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
            <h4 style="color: #ffffff; margin-bottom: 0.5rem;">{txt['step4_title']}</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">{txt['step4_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # CTA Section
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%); border-radius: 24px; border: 1px solid rgba(6, 182, 212, 0.3); margin: 3rem 0; direction: {direction};">
        <h2 style="font-size: 2.5rem; font-weight: 900; margin-bottom: 1rem; color: #ffffff;">
            {txt['cta_title']}
        </h2>
        <p style="color: #94a3b8; font-size: 1.2rem; margin-bottom: 2rem;">
            {txt['cta_subtitle']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(txt['cta_button'], type="primary", use_container_width=True, key="cta_button"):
            st.session_state.show_landing = False
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0; border-top: 1px solid rgba(255, 255, 255, 0.1); margin-top: 4rem; direction: {direction};">
        <p style="color: #64748b; font-size: 0.9rem;">
            {txt['footer_copyright']}
        </p>
        <p style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;">
            {txt['footer_features']}
        </p>
    </div>
    """, unsafe_allow_html=True)
