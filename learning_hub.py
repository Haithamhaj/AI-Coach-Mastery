import streamlit as st
import json
import os
from knowledge_bot import KnowledgeEngine
from icf_data_arabic import COMPETENCIES_AR
from grow_model_data import GROW_MODEL_EN, GROW_MODEL_AR

def show(api_key, language="English"):
    """
    Displays the Learning Hub & AI Tutor.
    """
    # Translations
    t = {
        "English": {
            "title": "📚 Learning Hub",
            "subtitle": "Master ICF Competencies, Markers, and GROW Model",
            "tab_comp": "Competencies",
            "tab_markers": "PCC Markers",
            "tab_grow": "GROW Model",
            "tab_tutor": "🤖 AI Tutor",
            "tutor_intro": "Ask me anything about ICF Standards or Coaching Skills!",
            "tutor_placeholder": "e.g., What is the difference between C6 and C7?",
            "chat_history": "Chat History",
            "clear_chat": "Clear Chat",
            "grow_g": "Goal",
            "grow_r": "Reality",
            "grow_o": "Options",
            "grow_w": "Will",
            "grow_desc": "The GROW model is a simple yet powerful framework for structuring coaching sessions.",
            "marker_search": "Search Markers...",
            "comp_select": "Select Competency"
        },
        "العربية": {
            "title": "📚 مركز المعرفة",
            "subtitle": "أتقن جدارات ICF، المؤشرات، ونموذج GROW",
            "tab_comp": "الجدارات",
            "tab_markers": "مؤشرات PCC",
            "tab_grow": "نموذج GROW",
            "tab_tutor": "🤖 المعلم الذكي",
            "tutor_intro": "اسألني أي شيء عن معايير ICF أو مهارات الكوتشينج!",
            "tutor_placeholder": "مثال: ما الفرق بين الجدارة 6 و 7؟",
            "chat_history": "سجل المحادثة",
            "clear_chat": "مسح المحادثة",
            "grow_g": "الهدف (Goal)",
            "grow_r": "الواقع (Reality)",
            "grow_o": "الخيارات (Options)",
            "grow_w": "الإرادة (Will)",
            "grow_desc": "نموذج GROW هو إطار عمل بسيط وقوي لتنظيم جلسات الكوتشينج.",
            "marker_search": "ابحث في المؤشرات...",
            "comp_select": "اختر الجدارة"
        }
    }
    
    txt = t[language]
    
    st.title(txt['title'])
    st.caption(txt['subtitle'])
    
    # Initialize Knowledge Engine
    if 'knowledge_engine' not in st.session_state:
        st.session_state.knowledge_engine = KnowledgeEngine(api_key)
        
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        txt['tab_comp'], 
        txt['tab_markers'], 
        txt['tab_grow'], 
        txt['tab_tutor']
    ])
    
    # --- TAB 1: COMPETENCIES ---
    with tab1:
        st.header(txt['tab_comp'])
        
        # Load Competencies
        if language == "العربية":
            comps = COMPETENCIES_AR
        else:
            comps = st.session_state.knowledge_engine.context_data.get('competencies', [])
        
        if not comps:
            st.error("Competencies data not found.")
        else:
            for comp in comps:
                with st.expander(f"{comp['id']}. {comp['name']}"):
                    desc_label = "التعريف" if language == "العربية" else "Description"
                    st.markdown(f"**{desc_label}:** {comp['definition']}")
                    
                    # Key Points
                    if 'key_points' in comp:
                        st.markdown("#### 💡 Key Points" if language == "English" else "#### 💡 نقاط رئيسية")
                        for point in comp['key_points']:
                            st.markdown(f"- {point}")
                            
                    # Common Mistakes
                    if 'common_mistakes' in comp:
                        st.markdown("#### ⚠️ Common Mistakes" if language == "English" else "#### ⚠️ أخطاء شائعة")
                        for mistake in comp['common_mistakes']:
                            st.markdown(f"- {mistake}")
                    
                    # Sub-competencies / Markers (if available in this view)
                    if 'sub_competencies' in comp:
                        st.markdown("#### 📋 Detailed Markers" if language == "English" else "#### 📋 تفاصيل الجدارة")
                        for sub in comp['sub_competencies']:
                            st.markdown(f"- **{sub['id']}**: {sub['text']}")
                    elif 'markers' in comp and comp['markers']:
                         st.markdown("#### 🎯 Markers" if language == "English" else "#### 🎯 المؤشرات")
                         for m in comp['markers']:
                             st.markdown(f"- **{m['id']}**: {m['text']}")

    # --- TAB 2: PCC MARKERS ---
    with tab2:
        st.header(txt['tab_markers'])
        
        # Load Markers
        if language == "العربية":
            markers_data = COMPETENCIES_AR # Structure matches
        else:
            markers_data = st.session_state.knowledge_engine.context_data.get('markers', [])
        
        if not markers_data:
            st.error("Markers data not found.")
        else:
            # Filter
            comp_names = [c['name'] for c in markers_data]
            selected_comp_name = st.selectbox(txt['comp_select'], ["All"] + comp_names)
            
            search_term = st.text_input(txt['marker_search'])
            
            for comp in markers_data:
                if selected_comp_name != "All" and comp['name'] != selected_comp_name:
                    continue
                
                # Check if any marker matches search
                comp_matches = False
                matching_markers = []
                
                for m in comp.get('markers', []):
                    if search_term.lower() in m['text'].lower() or search_term.lower() in m['id'].lower():
                        comp_matches = True
                        matching_markers.append(m)
                
                if comp_matches or not search_term:
                    st.subheader(f"{comp['id']}: {comp['name']}")
                    markers_to_show = matching_markers if search_term else comp.get('markers', [])
                    
                    for m in markers_to_show:
                        st.info(f"**{m['id']}**: {m['text']}")

    # --- TAB 3: GROW MODEL ---
    with tab3:
        st.header(txt['tab_grow'])
        st.write(txt['grow_desc'])
        
        # Select Data based on Language
        grow_data = GROW_MODEL_AR if language == "العربية" else GROW_MODEL_EN
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Helper to render GROW card
        def render_grow_card(column, phase_key, color_func):
            phase = grow_data[phase_key]
            with column:
                color_func(f"### {phase['name']}")
                st.write(f"**{phase['description']}**")
                st.markdown(f"{phase['details']}")
                
                with st.expander("💡 Tips & Mistakes" if language == "English" else "💡 نصائح وأخطاء"):
                    st.markdown("#### 💡 Tips" if language == "English" else "#### 💡 نصائح")
                    for point in phase['key_points']:
                        st.markdown(f"- {point}")
                        
                    st.markdown("#### ⚠️ Mistakes" if language == "English" else "#### ⚠️ أخطاء")
                    for mistake in phase['common_mistakes']:
                        st.markdown(f"- {mistake}")

                with st.expander("Questions" if language == "English" else "أسئلة مقترحة"):
                    for q in phase['questions']:
                        st.markdown(f"- {q}")

        render_grow_card(col1, "G", st.success)
        render_grow_card(col2, "R", st.warning)
        render_grow_card(col3, "O", st.info)
        render_grow_card(col4, "W", st.error)

    # --- TAB 4: AI TUTOR ---
    with tab4:
        st.header(txt['tab_tutor'])
        st.info(txt['tutor_intro'])
        
        # Chat History
        if "tutor_messages" not in st.session_state:
            st.session_state.tutor_messages = []
            
        # Display Chat
        for msg in st.session_state.tutor_messages:
            role = msg["role"]
            content = msg["content"]
            with st.chat_message(role):
                st.write(content)
                
        # Chat Input
        if prompt := st.chat_input(txt['tutor_placeholder']):
            # Add user message
            st.session_state.tutor_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
                
            # Generate Answer
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.knowledge_engine.ask_tutor(prompt, language)
                    st.write(response)
                    st.session_state.tutor_messages.append({"role": "assistant", "content": response})
                    
        # Clear Chat
        if st.button(txt['clear_chat']):
            st.session_state.tutor_messages = []
            st.rerun()
