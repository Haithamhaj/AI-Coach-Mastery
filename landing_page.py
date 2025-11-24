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
    """Display the landing page with embedded original HTML"""
    
    # Hide sidebar and adjust layout
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        /* Hide Streamlit header/footer */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* Ensure iframe takes full width */
        iframe {
            width: 100% !important;
            height: 100vh !important;
        }
        </style>
    """, unsafe_allow_html=True)

    try:
        # Read the original HTML file
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # --- Embed Images as Base64 ---
        # This fixes the missing images issue on Streamlit Cloud
        
        # 1. Logo
        logo_b64 = get_image_base64("logo.jpg")
        if logo_b64:
            html_content = html_content.replace('src="logo.jpg"', f'src="data:image/jpeg;base64,{logo_b64}"')
            
        # 2. Feature Images
        for img_name in ["feature1.png", "feature2.png", "feature3.png"]:
            img_b64 = get_image_base64(img_name)
            if img_b64:
                html_content = html_content.replace(f'src="{img_name}"', f'src="data:image/png;base64,{img_b64}"')

        # --- Inject JavaScript for Interaction ---
        script_to_inject = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Find all CTA buttons
                const buttons = document.querySelectorAll('a[href="#login"], button, .cta-button');
                buttons.forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        // If it's a login/start button
                        if (btn.innerText.includes('ابدأ') || btn.innerText.includes('Start') || btn.getAttribute('href') === '#login') {
                            e.preventDefault();
                            // Send message to Streamlit
                            window.parent.postMessage({type: 'streamlit:set_component_value', value: 'start_login'}, '*');
                        }
                    });
                });
            });
        </script>
        """
        
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", script_to_inject + "</body>")
        else:
            html_content += script_to_inject

        # Display the HTML
        import streamlit.components.v1 as components
        
        # Render HTML with full height
        components.html(html_content, height=1200, scrolling=True)
        
        # --- Floating Login Button (Fallback) ---
        # Only show this if user scrolls down or as a persistent option
        st.markdown("""
        <style>
        .floating-login-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 99999;
            background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
            padding: 12px 24px;
            border-radius: 50px;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
            border: 1px solid rgba(255,255,255,0.2);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # We use a container to place the button
        with st.container():
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                # Centered button at the bottom as a clear entry point
                if st.button("🚀 تسجيل الدخول / Login", type="primary", use_container_width=True):
                    st.session_state.show_landing = False
                    st.rerun()

    except FileNotFoundError:
        st.error("ملف التصميم الأصلي (index.html) غير موجود.")
        if st.button("Login"):
            st.session_state.show_landing = False
            st.rerun()
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(6, 182, 212, 0.1); border-radius: 12px; border: 1px solid rgba(6, 182, 212, 0.3); direction: {direction};">
            <div style="font-size: 2.5rem; font-weight: 900; color: #06b6d4;">{txt['stat2_num']}</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">{txt['stat2_label']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(6, 182, 212, 0.1); border-radius: 12px; border: 1px solid rgba(6, 182, 212, 0.3); direction: {direction};">
            <div style="font-size: 2.5rem; font-weight: 900; color: #06b6d4;">{txt['stat3_num']}</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">{txt['stat3_label']}</div>
        </div>
        """, unsafe_allow_html=True)
    
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
