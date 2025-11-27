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
            # 1. Selection Area (Interactive Cards)
            if 'selected_comp_id' not in st.session_state:
                st.session_state.selected_comp_id = comps[0]['id']

            st.markdown("### " + ("Select a Competency" if language == "English" else "اختر جدارة"))
            
            # Create rows of 4
            cols = st.columns(4)
            for i, c in enumerate(comps):
                with cols[i % 4]:
                    # Highlight the selected one? Streamlit buttons don't support active state styling easily, 
                    # but we can use the label or disabled state to indicate selection if needed.
                    # For now, just standard buttons.
                    if st.button(f"📘 {c['id']}", key=f"comp_btn_{c['id']}", use_container_width=True, help=c['name']):
                        st.session_state.selected_comp_id = c['id']
            
            # Find selected competency data
            selected_comp = next((c for c in comps if c['id'] == st.session_state.selected_comp_id), comps[0])
            
            st.markdown("---")
            
            # 2. Detailed View
            st.header(f"📘 {selected_comp['name']}")
            
            # Definition Box
            desc_label = "التعريف" if language == "العربية" else "Definition"
            st.info(f"**{desc_label}:** {selected_comp['definition']}")
            
            # Tabs for Details
            c_tab1, c_tab2, c_tab3 = st.tabs([
                "💡 " + ("Key Points" if language == "English" else "نقاط رئيسية"),
                "⚠️ " + ("Mistakes" if language == "English" else "أخطاء شائعة"),
                "🎯 " + ("Markers" if language == "English" else "المؤشرات")
            ])
            
            with c_tab1:
                if 'key_points' in selected_comp:
                    for point in selected_comp['key_points']:
                        st.success(f"**•** {point}")
                else:
                    st.caption("No key points available.")

            with c_tab2:
                if 'common_mistakes' in selected_comp:
                    for mistake in selected_comp['common_mistakes']:
                        st.warning(f"**•** {mistake}")
                else:
                    st.caption("No common mistakes listed.")

            with c_tab3:
                if 'sub_competencies' in selected_comp:
                    for sub in selected_comp['sub_competencies']:
                        st.info(f"**{sub['id']}**\n\n{sub['text']}")
                elif 'markers' in selected_comp and selected_comp['markers']:
                    for m in selected_comp['markers']:
                        st.info(f"**{m['id']}**\n\n{m['text']}")
                else:
                    st.caption("No markers available.")

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
            # Initialize selection state
            if 'selected_marker_comp' not in st.session_state:
                st.session_state.selected_marker_comp = "All"

            # Competency Grid (Cards)
            st.markdown("### " + ("Select a Competency" if language == "English" else "اختر جدارة"))
            
            # Create rows of 4
            cols = st.columns(4)
            for i, comp in enumerate(markers_data):
                with cols[i % 4]:
                    # Shorten name for button if needed, or use full
                    btn_label = f"{comp['id']}"
                    if st.button(f"📘 {comp['id']}", key=f"btn_{comp['id']}", use_container_width=True, help=comp['name']):
                        st.session_state.selected_marker_comp = f"{comp['id']}. {comp['name']}"
            
            # Show selected competency name
            if st.session_state.selected_marker_comp != "All":
                st.info(f"**Selected:** {st.session_state.selected_marker_comp}")
                if st.button("Show All" if language == "English" else "عرض الكل"):
                     st.session_state.selected_marker_comp = "All"
                     st.rerun()

            st.markdown("---")
            
            # Search (Hidden by default)
            with st.expander("🔍 " + ("Search specific marker..." if language == "English" else "البحث عن مؤشر محدد...")):
                search_term = st.text_input("Search", label_visibility="collapsed", placeholder="Type to search...")
            
            # Display Logic
            found_any = False
            for comp in markers_data:
                # Filter check
                comp_label = f"{comp['id']}. {comp['name']}"
                if st.session_state.selected_marker_comp != "All" and comp_label != st.session_state.selected_marker_comp:
                    continue
                
                # Search check (filter markers inside comp)
                matching_markers = []
                for m in comp.get('markers', []):
                    if search_term:
                        if search_term.lower() in m['text'].lower() or search_term.lower() in m['id'].lower():
                            matching_markers.append(m)
                    else:
                        matching_markers.append(m)
                
                if matching_markers:
                    found_any = True
                    # Competency Header
                    st.markdown(f"### 📘 {comp['name']}")
                    st.caption(comp['definition'])
                    
                    # Grid Layout for Markers
                    cols = st.columns(2) # 2 cards per row
                    for i, m in enumerate(matching_markers):
                        with cols[i % 2]:
                            st.info(f"**{m['id']}**\n\n{m['text']}")
            
            if not found_any:
                st.warning("No markers found matching your criteria.")
            
            if not found_any:
                st.warning("No markers found matching your criteria.")

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
