import streamlit as st
import time
from training_engine import TrainingEngine

def show(api_key, markers_data, language="English"):
    """
    Displays the 'Spot-It Pro' Arcade Game.
    """
    
    # Translations
    t = {
        "English": {
            "title": "🧩 Spot-It Pro: The Arcade",
            "subtitle": "Master ICF Competencies & Markers in a fast-paced game!",
            "score": "Score",
            "streak": "Streak",
            "level": "Level",
            "loading": "Generating new scenario...",
            "context": "Context",
            "client_says": "Client Says",
            "coach_says": "Coach Says",
            "question_1": "1. Which Competency is this?",
            "question_2": "2. Which Marker is demonstrated?",
            "question_3": "3. Which GROW Phase is this?",
            "submit": "Submit Answers",
            "next_round": "Next Round ➡️",
            "correct": "Correct! 🎉",
            "incorrect": "Incorrect",
            "explanation": "Why?",
            "game_over": "Game Over!",
            "final_score": "Final Score",
            "play_again": "Play Again",
            "start_game": "Start Game",
            "instructions": """
            **How to Play:**
            1. You will see a coaching scenario (Client statement + Coach response).
            2. Identify the **Competency**, **Marker**, and **GROW Phase**.
            3. Earn points for correct answers. Build your streak!
            """
        },
        "العربية": {
            "title": "🧩 سبوت-إت برو: الأركيد",
            "subtitle": "أتقن جدارات ومؤشرات ICF في لعبة سريعة!",
            "score": "النقاط",
            "streak": "تتابع الفوز",
            "level": "المستوى",
            "loading": "جاري توليد سيناريو جديد...",
            "context": "السياق",
            "client_says": "العميل يقول",
            "coach_says": "الكوتش يقول",
            "question_1": "1. ما هي الجدارة؟",
            "question_2": "2. ما هو المؤشر الظاهر؟",
            "question_3": "3. أي مرحلة من GROW؟",
            "submit": "إرسال الإجابات",
            "next_round": "الجولة التالية ➡️",
            "correct": "صحيح! 🎉",
            "incorrect": "غير صحيح",
            "explanation": "💡 تفسير الإجابة",
            "game_over": "انتهت اللعبة!",
            "final_score": "النتيجة النهائية",
            "play_again": "العب مجدداً",
            "start_game": "ابدأ اللعبة",
            "instructions": """
            **طريقة اللعب:**
            1. ستظهر لك حالة كوتشينج (كلام العميل + رد الكوتش).
            2. حدد **الجدارة**، **المؤشر**، و **مرحلة GROW**.
            3. اكسب نقاط للإجابات الصحيحة. حافظ على سلسلة الفوز!
            """
        }
    }
    
    txt = t[language]
    
    # Initialize Session State for Game
    if 'arcade_score' not in st.session_state:
        st.session_state.arcade_score = 0
    if 'arcade_streak' not in st.session_state:
        st.session_state.arcade_streak = 0
    if 'arcade_scenario' not in st.session_state:
        st.session_state.arcade_scenario = None
    if 'arcade_feedback' not in st.session_state:
        st.session_state.arcade_feedback = None
    
    # Header
    st.title(txt['title'])
    st.caption(txt['subtitle'])
    
    # Scoreboard
    c1, c2, c3 = st.columns(3)
    c1.metric(txt['score'], st.session_state.arcade_score)
    c2.metric(txt['streak'], f"🔥 {st.session_state.arcade_streak}")
    
    # Determine Difficulty based on streak
    difficulty = "Level 1"
    if st.session_state.arcade_streak > 3:
        difficulty = "Level 2"
    if st.session_state.arcade_streak > 7:
        difficulty = "Level 3"
    
    c3.metric(txt['level'], difficulty)
    
    st.markdown("---")
    
    # Start / Next Round Logic
    if st.session_state.arcade_scenario is None:
        if st.button(txt['start_game'] if st.session_state.arcade_score == 0 else txt['next_round'], type="primary"):
            if not api_key:
                st.error("API Key missing.")
                return
            
            trainer = TrainingEngine(api_key, markers_data)
            with st.spinner(txt['loading']):
                # Generate Scenario
                scenario_data = trainer.generate_learning_scenario(language=language, difficulty=difficulty)
                
                if "error" in scenario_data:
                    st.error(f"Error: {scenario_data['error']}")
                else:
                    st.session_state.arcade_scenario = scenario_data
                    st.session_state.arcade_feedback = None
                    st.rerun()
        else:
            if st.session_state.arcade_score == 0:
                st.info(txt['instructions'])
    
    # Display Game Board
    else:
        scenario_data = st.session_state.arcade_scenario
        # The 'scenario' key contains the context/statements
        scenario = scenario_data.get('scenario', {})
        
        # 1. The Scenario Card
        with st.container():
            st.caption(f"{txt['context']}")
            st.info(f"_{scenario.get('context', '')}_")
            
            col_chat_1, col_chat_2 = st.columns([1, 10])
            with col_chat_1:
                st.write("👤")
            with col_chat_2:
                st.markdown(f"**{txt['client_says']}:**")
                st.warning(f"\"{scenario.get('client_statement', '')}\"")
            
            col_chat_3, col_chat_4 = st.columns([1, 10])
            with col_chat_3:
                st.write("🎓")
            with col_chat_4:
                st.markdown(f"**{txt['coach_says']}:**")
                st.success(f"\"{scenario.get('coach_response', '')}\"")
        
        st.markdown("---")
        
        # 2. Input Form
        if st.session_state.arcade_feedback is None:
            with st.form("game_form"):
                # Prepare Options
                correct = scenario_data.get('correct_answers', {})
                distractors = scenario_data.get('distractors', {})
                
                # Competency Options
                comp_options = [correct.get('competency')] + distractors.get('competencies', [])
                # Shuffle options (simple shuffle)
                import random
                random.shuffle(comp_options)
                selected_comp = st.radio(txt['question_1'], comp_options)
                
                # Marker Options
                marker_options = [correct.get('marker')] + distractors.get('markers', [])
                random.shuffle(marker_options)
                selected_marker = st.radio(txt['question_2'], marker_options)
                
                # GROW Options
                grow_options = [correct.get('grow_phase')] + distractors.get('grow_phases', [])
                random.shuffle(grow_options)
                selected_grow = st.radio(txt['question_3'], grow_options)
                
                submitted = st.form_submit_button(txt['submit'], use_container_width=True, type="primary")
                
                if submitted:
                    # Check Answers
                    correct_comp = correct.get('competency')
                    correct_marker = correct.get('marker')
                    correct_grow = correct.get('grow_phase')
                    
                    is_correct_comp = (selected_comp == correct_comp)
                    is_correct_marker = (selected_marker == correct_marker)
                    is_correct_grow = (selected_grow == correct_grow)
                    
                    # Calculate Score
                    points = 0
                    if is_correct_comp: points += 10
                    if is_correct_marker: points += 10
                    if is_correct_grow: points += 10
                    
                    # Bonus for all correct
                    all_correct = is_correct_comp and is_correct_marker and is_correct_grow
                    if all_correct:
                        points += 20
                        st.session_state.arcade_streak += 1
                    else:
                        st.session_state.arcade_streak = 0
                    
                    st.session_state.arcade_score += points
                    
                    # Save Feedback
                    st.session_state.arcade_feedback = {
                        "is_correct_comp": is_correct_comp,
                        "is_correct_marker": is_correct_marker,
                        "is_correct_grow": is_correct_grow,
                        "correct_comp": correct_comp,
                        "correct_marker": correct_marker,
                        "correct_grow": correct_grow,
                        "explanation": scenario.get('explanation', ''),
                        "points_earned": points
                    }
                    st.rerun()
        
        # 3. Feedback Display
        else:
            fb = st.session_state.arcade_feedback
            
            # Result Alert
            if fb['points_earned'] > 0:
                st.success(f"You earned {fb['points_earned']} points!")
            else:
                st.error("No points this round.")
            
            c1, c2, c3 = st.columns(3)
            
            # Competency Result
            with c1:
                st.markdown(f"**{txt['question_1']}**")
                if fb['is_correct_comp']:
                    st.success(f"✅ {fb['correct_comp']}")
                else:
                    st.error(f"❌ {fb['correct_comp']}")
            
            # Marker Result
            with c2:
                st.markdown(f"**{txt['question_2']}**")
                if fb['is_correct_marker']:
                    st.success(f"✅ {fb['correct_marker']}")
                else:
                    st.error(f"❌ {fb['correct_marker']}")
            
            # GROW Result
            with c3:
                st.markdown(f"**{txt['question_3']}**")
                if fb['is_correct_grow']:
                    st.success(f"✅ {fb['correct_grow']}")
                else:
                    st.error(f"❌ {fb['correct_grow']}")
            
            # Explanation
            explanation_text = fb.get('explanation', '')
            if not explanation_text:
                explanation_text = "No explanation provided." if language == "English" else "لا يوجد تفسير متاح."
            
            st.info(f"**{txt['explanation']}:**\n\n{explanation_text}")
            
            # Next Button
            if st.button(txt['next_round'], type="primary", use_container_width=True):
                st.session_state.arcade_scenario = None
                st.session_state.arcade_feedback = None
                st.rerun()
