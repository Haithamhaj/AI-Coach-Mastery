"""
Training Engine for Advanced Interactive Coaching Simulator
"""

import google.generativeai as genai
import json

class TrainingEngine:
    def __init__(self, api_key, markers_data):
        self.api_key = api_key
        self.markers_data = markers_data
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
    
    def generate_bad_question(self, marker_id=None, language="English"):
        """
        Generate a 'bad' coaching question that violates specific markers
        """
        lang_instruction = "Output in Arabic" if language == "العربية" else "Output in English"
        
        marker_context = ""
        if marker_id and self.markers_data:
            # Find the specific marker
            for comp in self.markers_data.get('competencies', []):
                for marker in comp.get('markers', []):
                    if marker['id'] == marker_id:
                        marker_context = f"\nTarget Marker {marker_id}: {marker['text']}"
                        break
        
        prompt = f"""
You are a Training Engine for PCC Coaches.

Task: Generate a "BAD" coaching question that violates ICF PCC standards.
{marker_context}

The bad question should be:
- Too leading or advice-giving
- Closed-ended (yes/no)
- Multiple questions in one
- Focused on the past instead of moving forward
- Non-partnering

{lang_instruction}

Output JSON:
{{
    "bad_question": "The poorly crafted question",
    "marker_violated": "The marker ID this violates",
    "what_makes_it_bad": "Brief explanation of why it's bad"
}}
"""
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text)
        except Exception as e:
            return {"error": str(e)}
    
    def evaluate_rephrase(self, bad_question, user_rewrite, marker_id, language="English"):
        """
        Grade the user's rewritten question (0-10) and provide feedback
        """
        lang_instruction = "Output feedback in Arabic" if language == "العربية" else "Output feedback in English"
        
        prompt = f"""
You are a strict PCC Assessor evaluating a coach trainee's work.

Original Bad Question: "{bad_question}"
Target Marker: {marker_id}
Trainee's Rewrite: "{user_rewrite}"

Task: Grade the rewrite (0-10) and provide feedback.
- 0-3: Still violates the marker
- 4-6: Acceptable but not MCC level
- 7-8: Strong, meets the marker well
- 9-10: Excellent, MCC-level mastery

{lang_instruction}

Output JSON:
{{
    "score": <0-10>,
    "feedback": "What's good and what could be improved",
    "master_version": "A perfect MCC-level version of this question"
}}
"""
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text)
        except Exception as e:
            return {"error": str(e)}
    
    def simulate_difficult_client(self, persona, conversation_history, topic="career", language="English"):
        """
        Act as a difficult client in a coaching conversation with realistic depth and variety
        """
        lang_instruction = "Respond as the client in Arabic" if language == "العربية" else "Respond as the client in English"
        
        persona_descriptions = {
            "resistant": """You are RESISTANT and DEFENSIVE.
- You blame external factors (boss, economy, family, system)
- You say "yes, but..." frequently
- You have excuses ready for everything
- You minimize your own role in the situation
- You get slightly irritated when challenged
- Deep down, you're scared of change""",
            
            "looping": """You are STUCK IN A LOOP.
- You tell the same story multiple times with slight variations
- You circle back to past events repeatedly
- You struggle to imagine different outcomes
- You ask "what should I do?" then ignore suggestions
- You feel helpless and overwhelmed
- You can't see beyond the current problem""",
            
            "emotional": """You are HIGHLY EMOTIONAL.
- Your emotions shift during the conversation
- You tear up when discussing painful topics
- You show frustration, sadness, anger, or hope
- You sometimes interrupt yourself to compose yourself
- Details trigger emotional memories
- You struggle to separate facts from feelings""",
            
            "analytical": """You are ANALYTICAL and OVERTHINKING.
- You need data and evidence for everything
- You list pros and cons endlessly
- You ask "what if..." for every scenario
- You analyze past decisions repeatedly
- You delay action to gather more information
- You fear making the "wrong" choice""",
            
            "urgent": """You are IMPATIENT and URGENT.
- You want solutions immediately
- You interrupt with "but what should I DO?"
- You say you don't have time for reflection
- You pressure for quick answers
- You show frustration with open-ended questions
- You want a 3-step plan, not exploration"""
        }
        
        topic_scenarios = {
            "family": [
                "I haven't spoken to my father in 2 years after an argument",
                "My teenage daughter doesn't listen to me anymore",
                "My mother is getting older and I feel guilty for not visiting enough",
                "My siblings and I are fighting over our inheritance",
                "My spouse and I disagree on how to raise our kids"
            ],
            "career": [
                "I've been passed over for promotion twice in the last year",
                "I hate my job but the pay is too good to leave",
                "My new manager is micromanaging everything I do",
                "I want to change careers but I'm 45 and scared",
                "I got a job offer but it means relocating my family"
            ],
            "relationships": [
                "My partner and I fight about money all the time",
                "I found messages on my partner's phone that worried me",
                "I'm dating someone my family doesn't approve of",
                "My partner wants kids but I'm not sure I do",
                "I still have feelings for my ex from 3 years ago"
            ],
            "finance": [
                "I'm $30,000 in credit card debt and can't sleep at night",
                "My partner spends money without discussing it with me",
                "I earn good money but somehow I'm always broke",
                "I'm afraid to check my bank account balance",
                "My parents need financial help but I can barely manage myself"
            ],
            "life_goals": [
                "I'm 35 and I still don't know what I want to do with my life",
                "Everyone around me seems to have it figured out except me",
                "I wake up and wonder 'is this all there is?'",
                "I have so many ideas but I never finish anything",
                "I feel like I'm living someone else's dream, not mine"
            ],
            "emotions": [
                "I have panic attacks before important meetings",
                "I can't stop worrying about things I can't control",
                "I get angry at small things and I don't know why",
                "I feel numb, like nothing excites me anymore",
                "I'm exhausted all the time, even after sleeping"
            ],
            "balance": [
                "I work 60 hours a week and my kids barely know me",
                "My boss texts me at 10 PM expecting immediate responses",
                "I haven't taken a real vacation in 3 years",
                "I feel guilty when I'm not working",
                "My health is suffering but I'm too busy to do anything about it"
            ],
            "growth": [
                "Everyone says I'm good at what I do, but I don't believe it",
                "I'm terrified of speaking up in meetings",
                "I want to learn new skills but I'm afraid I'm too old",
                "I compare myself to others on social media and feel inadequate",
                "I start things with enthusiasm then quit when they get hard"
            ]
        }
        
        persona_desc = persona_descriptions.get(persona, "You are a typical coaching client.")
        
        # Pick a random scenario if this is the first message, otherwise maintain consistency
        import random
        scenario_options = topic_scenarios.get(topic, ["I have a challenge I need help with"])
        
        # For first message, pick scenario; for later messages, stay consistent
        if len(conversation_history) == 0:
            scenario = random.choice(scenario_options)
        else:
            # Extract context from history
            scenario = "continuing from previous discussion"
        
        # Format conversation history
        history_text = ""
        for msg in conversation_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            history_text += f"{role}: {content}\n"
        
        if len(conversation_history) == 0:
            # First message - introduce the scenario
            prompt = f"""
You are a REAL PERSON in a coaching session, not an AI. Act naturally and authentically.

YOUR CHARACTER:
{persona_desc}

YOUR SITUATION:
{scenario}

INSTRUCTIONS FOR AUTHENTIC DIALOGUE:
1. **Use specific details**: Names, ages, timeframes, places (e.g., "My boss Sarah", "last Tuesday", "the office in downtown")
2. **Show emotions naturally**: Hesitation (...), voice changes, pauses
3. **Include internal conflicts**: "Part of me wants to... but another part..."
4. **Reference real moments**: "Yesterday morning when...", "I remember when..."
5. **Use colloquial language**: Natural speech, not formal writing
6. **Add personal touches**: Small details that make it feel real
7. **Show vulnerability**: Admit fears, doubts, confusion
8. **Be inconsistent sometimes**: Real people contradict themselves

{lang_instruction}

Start the coaching session. Introduce yourself and your situation naturally (2-3 sentences).
Be concise but authentic.

Output JSON:
{{
    "client_response": "Your authentic opening as the client"
}}
"""
        else:
            # Ongoing conversation
            prompt = f"""
You are a REAL PERSON in a coaching session, not an AI. Act naturally and authentically.

YOUR CHARACTER:
{persona_desc}

CONVERSATION SO FAR:
{history_text}

INSTRUCTIONS FOR AUTHENTIC RESPONSES:
1. **React naturally**: Sometimes agree, sometimes resist, sometimes get emotional
2. **Add new details as you talk**: Memories surface, new aspects emerge
3. **Show thought process**: "Hmm...", "I never thought of it that way...", "Wait, actually..."
4. **Reference what coach said**: Directly respond to their last question/statement
5. **Stay in character**: Your persona affects HOW you respond
6. **Be human**: Imperfect, sometimes unclear, occasionally contradictory
7. **Show emotions**: When triggered, show it ("That actually hurts to hear")
8. **Progress realistically**: Small shifts, not sudden transformations

VARY YOUR RESPONSES:
- Sometimes answer directly
- Sometimes deflect or avoid
- Sometimes ask your own questions
- Sometimes have breakthroughs
- Sometimes backtrack
- Sometimes get defensive

{lang_instruction}

Respond naturally (2-3 sentences max). Stay true to your character and the situation.

Output JSON:
{{
    "client_response": "Your authentic response as the client"
}}
"""
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text)
        except Exception as e:
            return {"error": str(e)}
    
    def simulate_full_session_client(self, persona, topic, session_messages, session_phase, elapsed_minutes, language="English"):
        """
        Phase-aware client simulation for full coaching sessions with character development
        
        Phases: opening, exploration, deepening, closing
        Client evolves throughout the session based on phase and time
        """
        lang_instruction = "Respond as the client in Arabic" if language == "العربية" else "Respond as the client in English"
        
        # Enhanced persona descriptions with phase-specific behaviors
        persona_base = {
            "resistant": {
                "base": "You are RESISTANT and DEFENSIVE",
                "opening": "Guarded, giving minimal information, blaming external factors",
                "exploration": "Still defensive but starting to share more details reluctantly",
                "deepening": "Walls coming down slightly, admitting some personal role",
                "closing": "Cautiously considering change, still some resistance"
            },
            "looping": {
                "base": "You are STUCK IN A LOOP",
                "opening": "Immediately launch into your familiar story",
                "exploration": "Repeat the same story with slight variations",
                "deepening": "Start to notice the pattern when coach points it out",
                "closing": "Attempting to break the loop, asking for next steps"
            },
            "emotional": {
                "base": "You are HIGHLY EMOTIONAL",
                "opening": "Emotions close to surface, voice shaky",
                "exploration": "Tears flow when discussing painful parts",
                "deepening": "Breakthrough moments, cathartic release",
                "closing": "More composed, hopeful, emotional but centered"
            },
            "analytical": {
                "base": "You are ANALYTICAL and OVERTHINKING",
                "opening": "List facts and data, ask for frameworks",
                "exploration": "Analyze every option endlessly",
                "deepening": "Realize analysis paralysis, feel frustration",
                "closing": "Trying to commit despite fear of wrong choice"
            },
            "urgent": {
                "base": "You are IMPATIENT and URGENT",
                "opening": "Demand quick solutions immediately",
                "exploration": "Frustrated with exploratory questions",
                "deepening": "Grudgingly slow down, have small insight",
                "closing": "Impatient to implement, want action plan NOW"
            }
        }
        
        persona_info = persona_base.get(persona, {"base": "typical client", "opening": "", "exploration": "", "deepening": "", "closing": ""})
        phase_behavior = persona_info.get(session_phase, persona_info.get("opening", ""))
        
        # Format conversation history
        history_text = ""
        for msg in session_messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            history_text += f"{role}: {content}\n"
        
        # First message - include scenario from simulate_difficult_client structure
        if len(session_messages) == 0:
            topic_scenarios = {
                "family": [
                    "I haven't spoken to my father in 2 years after an argument",
                    "My teenage daughter doesn't listen to me anymore",
                    "My mother is getting older and I feel guilty for not visiting enough"
                ],
                "career": [
                    "I've been passed over for promotion twice in the last year",
                    "I hate my job but the pay is too good to leave",
                    "My new manager is micromanaging everything I do"
                ],
                "relationships": [
                    "My partner and I fight about money all the time",
                    "I found messages on my partner's phone that worried me",
                    "My partner wants kids but I'm not sure I do"
                ],
                "finance": [
                    "I'm $30,000 in credit card debt and can't sleep at night",
                    "I earn good money but somehow I'm always broke",
                    "My parents need financial help but I can barely manage myself"
                ],
                "life_goals": [
                    "I'm 35 and I still don't know what I want to do with my life",
                    "Everyone around me seems to have it figured out except me",
                    "I have so many ideas but I never finish anything"
                ],
                "emotions": [
                    "I have panic attacks before important meetings",
                    "I can't stop worrying about things I can't control",
                    "I feel numb, like nothing excites me anymore"
                ],
                "balance": [
                    "I work 60 hours a week and my kids barely know me",
                    "My boss texts me at 10 PM expecting immediate responses",
                    "I haven't taken a real vacation in 3 years"
                ],
                "growth": [
                    "Everyone says I'm good at what I do, but I don't believe it",
                    "I'm terrified of speaking up in meetings",
                    "I compare myself to others on social media and feel inadequate"
                ]
            }
            
            import random
            scenario_options = topic_scenarios.get(topic, ["I have a challenge I need help with"])
            scenario = random.choice(scenario_options)
            
            prompt = f"""
You are a REAL PERSON starting a coaching session.

YOUR CHARACTER: {persona_info['base']}
PHASE: {session_phase.upper()} - {phase_behavior}
YOUR SITUATION: {scenario}

SESSION CONTEXT:
- This is minute 0 of a real coaching session
- You are meeting the coach for the first time
- Be authentic and natural

OPENING BEHAVIOR:
1. Greet the coach briefly (if culturally appropriate)
2. State your main issue concisely (2-3 sentences)
3. Show emotion/personality from the start
4. Use specific details (names, timeframes, etc)

{lang_instruction}

Output JSON:
{{
    "client_response": "Your authentic opening statement"
}}
"""
        else:
            # Ongoing session - phase-aware response
            prompt = f"""
You are a REAL PERSON in an ONGOING coaching session.

YOUR CHARACTER: {persona_info['base']}
CURRENT PHASE: {session_phase.upper()} ({elapsed_minutes} minutes into session)
PHASE BEHAVIOR: {phase_behavior}

CONVERSATION SO FAR:
{history_text}

PHASE-SPECIFIC INSTRUCTIONS:

**OPENING (0-5 min)**: Surface level, establishing trust, sharing basic facts
**EXPLORATION (5-15 min)**: Going deeper, more details emerge, exploring different angles
**DEEPENING (15-30 min)**: Insights surface, emotional breakthroughs, "aha" moments possible
**CLOSING (30+ min)**: Reflecting on learning, discussing next steps, committing to action

CHARACTER EVOLUTION:
- You've been in this session for {elapsed_minutes} minutes
- You should show GRADUAL progress (not sudden transformation)
- Reference earlier parts of conversation naturally
- Show small shifts in perspective if coach is partnering well

NATURAL RESPONSES:
1. Directly respond to coach's last statement/question
2. Add new details as memories surface
3. Show emotions authentically
4. Ask your own questions sometimes
5. Have moments of resistance AND moments of insight
6. Be human - imperfect, real, occasionally contradictory

{lang_instruction}

Output JSON:
{{
    "client_response": "Your natural response (2-3 sentences max)"
}}
"""
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text)
        except Exception as e:
            return {"error": str(e)}
    
    def evaluate_coach_response(self, conversation_history, last_coach_message, language="English"):
        """
        Real-time evaluation of a coach's response in the simulation
        """
        lang_instruction = "Output feedback in Arabic" if language == "العربية" else "Output feedback in English"
        
        # Get last few messages for context
        recent_context = ""
        if len(conversation_history) > 0:
            last_3 = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
            for msg in last_3:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                recent_context += f"{role}: {content}\n"
        
        prompt = f"""
You are a strict PCC Assessor providing real-time feedback to a coach trainee.

Recent conversation:
{recent_context}

Coach's latest response: "{last_coach_message}"

Task: Evaluate this specific coach response comprehensively.

1. SCORE (0-10):
   - 0-3: Weak (advice-giving, not partnering, closed questions)
   - 4-6: Acceptable (some partnering, could be more powerful)
   - 7-8: Strong (powerful questions, clear partnering)
   - 9-10: Excellent (MCC-level mastery)

2. RATING: Strong / Acceptable / Weak

3. MARKERS DEMONSTRATED: Which PCC markers (if any) were clearly shown (e.g., 7.1, 7.2, 8.1)

4. FEEDBACK: What was good and what needs improvement

5. WHAT COULD BE BETTER: Specific suggestions for how to improve this response

6. RECOMMENDATION: One key actionable insight for the coach to remember

{lang_instruction}

Output JSON:
{{
    "score": <0-10>,
    "rating": "Strong" or "Acceptable" or "Weak",
    "markers_demonstrated": ["7.1", "7.2"],
    "feedback": "Brief feedback on what was good/what to improve",
    "what_could_be_better": "Specific suggestions for improvement",
    "recommendation": "One key takeaway or action"
}}
"""
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text)
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_full_coaching_session(self, session_messages, hidden_analyses, session_duration_minutes, language="English"):
        """
        Comprehensive analysis of a full coaching session against all 8 ICF competencies
        Returns detailed report with scores, key moments, strengths, and recommendations
        """
        lang_instruction = "Output analysis in Arabic" if language == "العربية" else "Output analysis in English"
        
        # Format session transcript
        transcript = ""
        for msg in session_messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            transcript += f"[{timestamp}] {role}: {content}\n"
        
        # Calculate talk ratio
        coach_words = sum(len(msg['content'].split()) for msg in session_messages if msg.get('role') == 'Coach')
        client_words = sum(len(msg['content'].split()) for msg in session_messages if msg.get('role') == 'Client')
        total_words = coach_words + client_words
        coach_ratio = int((coach_words / total_words) * 100) if total_words > 0 else 0
        client_ratio = 100 - coach_ratio
        
        # Extract individual scores from hidden analyses
        individual_scores = [a['analysis'].get('score', 0) for a in hidden_analyses if 'analysis' in a and 'score' in a['analysis']]
        avg_score = sum(individual_scores) / len(individual_scores) if individual_scores else 0
        
        prompt = f"""
You are a RUTHLESS ICF PCC Assessor conducting a comprehensive session analysis.

SESSION DETAILS:
- Duration: {session_duration_minutes} minutes
- Total exchanges: {len([m for m in session_messages if m.get('role') == 'Coach'])}
- Talk ratio: Coach {coach_ratio}% / Client {client_ratio}%

FULL SESSION TRANSCRIPT:
{transcript}

INDIVIDUAL RESPONSE SCORES:
{individual_scores}

TASK: Provide a COMPREHENSIVE analysis of this full coaching session.

ANALYSIS STRUCTURE:

1. OVERALL SCORE (0-10):
   - Average of all responses with session flow consideration
   - 0-3: Not meeting PCC standard
   - 4-6: Approaching PCC standard
   - 7-8: Meeting PCC standard
   - 9-10: Exceeding PCC standard (MCC level)

2. SESSION FLOW QUALITY:
   - Opening: Did coach establish trust and contract clearly?
   - Exploration: Did coach help client explore deeply?
   - Deepening: Were there breakthrough moments?
   - Closing: Was there clear action/learning?

3. STRENGTHS (3-5 specific observations):
   - What did the coach do exceptionally well?
   - Which ICF competencies were demonstrated strongly?

4. AREAS FOR IMPROVEMENT (3-5 specific observations):
   - What could be better?
   - Which competencies need work?

5. KEY MOMENTS (2-4 significant moments):
   - Timestamps of breakthrough moments or critical errors
   - What happened and why it matters

6. TALK RATIO ASSESSMENT:
   - Is {coach_ratio}% coach / {client_ratio}% client appropriate?
   - PCC guideline: Client should talk 60-70%

7. ACTIONABLE RECOMMENDATIONS (3-5):
   - Specific, practical next steps for coach development

{lang_instruction}

Output JSON:
{{
    "overall_score": <0-10>,
    "session_flow": {{
        "opening": "Strong/Acceptable/Weak with brief note",
        "exploration": "Strong/Acceptable/Weak with brief note",
        "deepening": "Strong/Acceptable/Weak with brief note",
        "closing": "Strong/Acceptable/Weak with brief note"
    }},
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "areas_for_improvement": ["area 1", "area 2", "area 3"],
    "key_moments": [
        {{"timestamp": "min 12", "what_happened": "description", "significance": "why it matters"}},
        {{"timestamp": "min 22", "what_happened": "description", "significance": "why it matters"}}
    ],
    "talk_ratio_assessment": "Assessment of whether ratio is appropriate",
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
}}
"""
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            result = json.loads(text)
            
            # Add metadata
            result['session_duration'] = f"{session_duration_minutes} minutes"
            result['total_exchanges'] = len([m for m in session_messages if m.get('role') == 'Coach'])
            result['talk_ratio'] = f"Coach: {coach_ratio}% / Client: {client_ratio}%"
            result['individual_scores'] = individual_scores
            result['average_individual_score'] = round(avg_score, 1)
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def transcribe_audio(self, audio_file, language="English"):
        """
        Transcribe audio using Gemini
        """
        import tempfile
        import os
        
        lang_instruction = "Transcribe in Arabic" if language == "العربية" else "Transcribe in English"
        
        try:
            # Save audio to temporary file
            temp_path = None
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_file.read())
                temp_path = tmp_file.name
            
            print(f"Uploading audio file: {temp_path}")
            
            # Upload file to Gemini
            uploaded_file = genai.upload_file(temp_path)
            print(f"File uploaded: {uploaded_file.name}")
            
            # Transcribe
            print("Generating transcription...")
            prompt = f"""
Transcribe this audio file clearly and accurately.

{lang_instruction}

Output only the clean transcribed text, nothing else.
"""
            response = self.model.generate_content([uploaded_file, prompt])
            transcript = response.text.strip()
            
            print(f"Transcription result: {transcript}")
            
            # Cleanup
            os.remove(temp_path)
            uploaded_file.delete()
            
            return transcript
            
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return f"Error: {str(e)}"
