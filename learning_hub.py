import streamlit as st
import json
import os
from knowledge_bot import KnowledgeEngine

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
        comps = st.session_state.knowledge_engine.context_data.get('competencies', [])
        
        if not comps:
            st.error("Competencies data not found.")
        else:
            for comp in comps:
                with st.expander(f"**{comp['id']}: {comp['name']}**"):
                    st.write(f"_{comp.get('description', '')}_")
                    
                    if 'sub_competencies' in comp: # 2025 format might have sub-items
                        for sub in comp['sub_competencies']:
                            st.markdown(f"- {sub}")
                    elif 'markers' in comp: # Fallback to markers if structure differs
                        st.markdown("**Markers:**")
                        for m in comp['markers']:
                            st.markdown(f"- **{m['id']}**: {m['text']}")

    # --- TAB 2: PCC MARKERS ---
    with tab2:
        st.header(txt['tab_markers'])
        
        # Load Markers
        # Assuming markers.json structure is {competencies: [{id, name, markers: []}]}
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
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.success(f"### {txt['grow_g']}")
            st.write("Defining the objective.")
            with st.expander("Questions"):
                st.markdown("- What do you want to achieve?\n- What is important about this?")
                
        with col2:
            st.warning(f"### {txt['grow_r']}")
            st.write("Exploring the current situation.")
            with st.expander("Questions"):
                st.markdown("- What is happening now?\n- What have you tried so far?")
                
        with col3:
            st.info(f"### {txt['grow_o']}")
            st.write("Generating ideas and strategies.")
            with st.expander("Questions"):
                st.markdown("- What could you do?\n- What are the pros/cons?")
                
        with col4:
            st.error(f"### {txt['grow_w']}")
            st.write("Committing to action.")
            with st.expander("Questions"):
                st.markdown("- What will you do?\n- When will you start?")

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
