import google.generativeai as genai
import json
import os

class KnowledgeEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            
        self.context_data = self._load_context()
        
    def _load_context(self):
        """
        Load ICF Competencies, Markers, and GROW model data into memory.
        """
        context = {
            "competencies": [],
            "markers": [],
            "grow_model": {}
        }
        
        # Load Competencies (2025)
        try:
            if os.path.exists('icf_core_competencies_2025.json'):
                with open('icf_core_competencies_2025.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    context["competencies"] = data.get('competencies', [])
        except Exception as e:
            print(f"Error loading competencies: {e}")
            
        # Load Markers
        try:
            if os.path.exists('markers.json'):
                with open('markers.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Flatten markers for easier search if needed, or keep structure
                    context["markers"] = data.get('competencies', [])
        except Exception as e:
            print(f"Error loading markers: {e}")
            
        # Define GROW Model Context
        context["grow_model"] = {
            "G": "Goal: Defining the objective. Questions: What do you want to achieve? What is important about this?",
            "R": "Reality: Exploring the current situation. Questions: What is happening now? What have you tried?",
            "O": "Options: Generating ideas. Questions: What could you do? What else?",
            "W": "Will: Committing to action. Questions: What will you do? When? How will you know?"
        }
        
        return context

    def ask_tutor(self, query, language="English"):
        """
        Ask the AI Tutor a question. Enforces strict topic guardrails.
        """
        if not self.api_key:
            return "Error: API Key missing."
            
        lang_instruction = "Answer in Arabic." if language == "العربية" else "Answer in English."
        
        # Prepare Context String
        competencies_text = json.dumps(self.context_data['competencies'], ensure_ascii=False)
        markers_text = json.dumps(self.context_data['markers'], ensure_ascii=False)
        grow_text = json.dumps(self.context_data['grow_model'], ensure_ascii=False)
        
        prompt = f"""
        You are an EXPERT ICF MENTOR COACH and AI TUTOR.
        
        YOUR KNOWLEDGE BASE:
        1. ICF Core Competencies (2025): {competencies_text}
        2. PCC Markers (2021): {markers_text}
        3. GROW Model: {grow_text}
        
        YOUR MISSION:
        Answer the user's question based ONLY on the provided knowledge base.
        
        STRICT GUARDRAILS:
        - You ONLY answer questions about: ICF Competencies, PCC Markers, Coaching Ethics, and the GROW Model.
        - If the user asks about ANYTHING ELSE (e.g., cooking, sports, coding, general life advice), you must POLITELY DECLINE.
        - Decline Message: "I specialize only in ICF Coaching Standards and the GROW Model. Please ask me about these topics." (Translate this if answering in Arabic).
        
        ANSWER STYLE:
        - Be educational, encouraging, and precise.
        - CITE SPECIFIC MARKERS or COMPETENCIES where relevant (e.g., "This relates to Marker 5.2...").
        - Use bullet points for readability.
        - Keep answers concise but complete.
        
        USER QUESTION: "{query}"
        
        {lang_instruction}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
