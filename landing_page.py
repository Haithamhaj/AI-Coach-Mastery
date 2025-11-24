"""
Landing Page for AI Coach Mastery
"""
import streamlit as st

def show_landing_page(language="English"):
    """Display the landing page"""
    
    # Hide sidebar for landing page
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        .main > div {
            padding-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div style="padding: 40px 0;">
            <h1 style="font-size: 3.5rem; font-weight: 900; margin-bottom: 1rem; background: linear-gradient(to right, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                AI Coach Mastery
            </h1>
            <h2 style="font-size: 2rem; font-weight: 700; margin-bottom: 1.5rem; color: #ffffff;">
                بوابتك لاحتراف الكوتشينج
            </h2>
            <p style="font-size: 1.2rem; color: #94a3b8; line-height: 1.8; margin-bottom: 2rem;">
                منصة ذكية تعمل كمقيم وموجه شخصي (Mentor)، تساعدك على إتقان جدارات ICF 
                وعلامات PCC الـ 37 من خلال التحليل الدقيق والمحاكاة الواقعية.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(6, 182, 212, 0.1); border-radius: 12px; border: 1px solid rgba(6, 182, 212, 0.3);">
                <div style="font-size: 2.5rem; font-weight: 900; color: #06b6d4;">37</div>
                <div style="color: #94a3b8; font-size: 0.9rem;">علامة PCC</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col2:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(6, 182, 212, 0.1); border-radius: 12px; border: 1px solid rgba(6, 182, 212, 0.3);">
                <div style="font-size: 2.5rem; font-weight: 900; color: #06b6d4;">8</div>
                <div style="color: #94a3b8; font-size: 0.9rem;">جدارات ICF</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col3:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(6, 182, 212, 0.1); border-radius: 12px; border: 1px solid rgba(6, 182, 212, 0.3);">
                <div style="font-size: 2.5rem; font-weight: 900; color: #06b6d4;">95%</div>
                <div style="color: #94a3b8; font-size: 0.9rem;">دقة التحليل</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Display logo
        try:
            st.image("logo.jpg", width=400)
        except:
            st.markdown("""
            <div style="width: 400px; height: 400px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 24px; display: flex; align-items: center; justify-content: center;">
                <div style="font-size: 4rem;">🧠</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features Section
    st.markdown("""
    <h2 style="text-align: center; font-size: 2.5rem; font-weight: 900; margin: 3rem 0 2rem 0; color: #ffffff;">
        ✨ المميزات الرئيسية
    </h2>
    """, unsafe_allow_html=True)
    
    feat1, feat2, feat3 = st.columns(3)
    
    with feat1:
        try:
            st.image("feature1.png", use_container_width=True)
        except:
            pass
        st.markdown("""
        <div style="padding: 1.5rem; background: rgba(15, 23, 42, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); height: 100%;">
            <h3 style="color: #06b6d4; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">
                📊 تحليل الجلسات المعمق
            </h3>
            <p style="color: #94a3b8; line-height: 1.6;">
                ارفع ملفاتك الصوتية أو النصية واحصل على تدقيق فوري للعلامات، 
                تحليل نسب التحدث، وكشف الفجوات في الأداء.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat2:
        try:
            st.image("feature2.png", use_container_width=True)
        except:
            pass
        st.markdown("""
        <div style="padding: 1.5rem; background: rgba(15, 23, 42, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); height: 100%;">
            <h3 style="color: #a855f7; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">
                🎭 محاكاة العملاء (AI Persona)
            </h3>
            <p style="color: #94a3b8; line-height: 1.6;">
                تدرب في بيئة آمنة مع عملاء افتراضيين بأنماط صعبة 
                (المقاوم، العاطفي، كثير التفكير) واحصل على توجيه لحظي.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat3:
        try:
            st.image("feature3.png", use_container_width=True)
        except:
            pass
        st.markdown("""
        <div style="padding: 1.5rem; background: rgba(15, 23, 42, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); height: 100%;">
            <h3 style="color: #f59e0b; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">
                🏆 تقييم PCC الموضوعي
            </h3>
            <p style="color: #94a3b8; line-height: 1.6;">
                تغذية راجعة حيادية وفورية تستند إلى 37 علامة سلوكية لـ ICF، 
                مما يسرع رحلتك نحو الاعتماد الدولي.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # How It Works
    st.markdown("""
    <h2 style="text-align: center; font-size: 2.5rem; font-weight: 900; margin: 3rem 0 2rem 0; color: #ffffff;">
        🚀 كيف يعمل
    </h2>
    """, unsafe_allow_html=True)
    
    step1, step2, step3, step4 = st.columns(4)
    
    with step1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; background: rgba(6, 182, 212, 0.1); border-radius: 16px; border: 1px solid rgba(6, 182, 212, 0.3);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📤</div>
            <h4 style="color: #ffffff; margin-bottom: 0.5rem;">ارفع جلستك</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">حمّل ملف صوتي أو نصي</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; background: rgba(139, 92, 246, 0.1); border-radius: 16px; border: 1px solid rgba(139, 92, 246, 0.3);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
            <h4 style="color: #ffffff; margin-bottom: 0.5rem;">تحليل ذكي</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">AI يحلل كل العلامات</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step3:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; background: rgba(245, 158, 11, 0.1); border-radius: 16px; border: 1px solid rgba(245, 158, 11, 0.3);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
            <h4 style="color: #ffffff; margin-bottom: 0.5rem;">تقرير مفصل</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">نقاط قوة وفجوات</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step4:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; background: rgba(34, 197, 94, 0.1); border-radius: 16px; border: 1px solid rgba(34, 197, 94, 0.3);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
            <h4 style="color: #ffffff; margin-bottom: 0.5rem;">تدرّب وتطوّر</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">محاكاة مستمرة</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%); border-radius: 24px; border: 1px solid rgba(6, 182, 212, 0.3); margin: 3rem 0;">
        <h2 style="font-size: 2.5rem; font-weight: 900; margin-bottom: 1rem; color: #ffffff;">
            جاهز لتصبح <span style="background: linear-gradient(to right, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">كوتش محترف؟</span>
        </h2>
        <p style="color: #94a3b8; font-size: 1.2rem; margin-bottom: 2rem;">
            ابدأ رحلتك نحو الاحتراف مع AI Coach Mastery - منصتك الذكية لإتقان معايير ICF
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 ابدأ الآن - Start Now", type="primary", use_container_width=True, key="cta_button"):
            st.session_state.show_landing = False
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; border-top: 1px solid rgba(255, 255, 255, 0.1); margin-top: 4rem;">
        <p style="color: #64748b; font-size: 0.9rem;">
            © 2024 AI Coach Mastery. جميع الحقوق محفوظة
        </p>
        <p style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;">
            ✓ تحليل دقيق للجلسات • ✓ محاكاة واقعية • ✓ تقييم فوري
        </p>
    </div>
    """, unsafe_allow_html=True)
