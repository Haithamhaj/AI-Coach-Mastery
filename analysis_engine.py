import google.generativeai as genai
import json
import os
import random
import time

class AnalysisEngine:
    def __init__(self, api_key, markers_data):
        self.api_key = api_key
        self.markers_data = markers_data
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Using 'latest' aliases as specific versions (1.5) are not found for this key
            self.model_flash = genai.GenerativeModel('gemini-flash-latest')
            self.model_pro = genai.GenerativeModel('gemini-pro-latest')

    def check_ethics(self, content, is_audio=False, language="English"):
        """
        Stage 1: Ethical Filter
        """
        if not self.api_key:
            return {"status": "ERROR", "reason": "API Key missing"}

        lang_instruction = "Output the 'reason' in Arabic." if language == "العربية" else "Output the 'reason' in English."

        prompt = f"""
        Role: You are an expert ICF Assessor and Ethical Gatekeeper.
        Task: Analyze the following coaching session specifically for violations of the ICF Code of Ethics (Competency 1).
        
        Look for:
        - Breaches of confidentiality.
        - Conflicts of interest.
        - Inappropriate boundaries.
        - Illegal activities.
        - Misleading claims.
        - Coach imposing their own agenda aggressively.
        
        Output Format:
        Return ONLY a JSON object:
        {{
            "status": "PASS" or "FAIL",
            "reason": "Explanation of why it passed or failed. {lang_instruction}"
        }}
        """
        
        try:
            if is_audio:
                response = self.model_pro.generate_content([prompt, content], generation_config={"response_mime_type": "application/json"})
            else:
                response = self.model_flash.generate_content(prompt + f"\n\nTranscript:\n{content}", generation_config={"response_mime_type": "application/json"})
            
            return json.loads(response.text)
        except Exception as e:
            return {"status": "ERROR", "reason": str(e)}

    def analyze_markers(self, content, is_audio=False, language="English"):
        """
        Stage 2: Marker Detection
        """
        if not self.api_key:
            return {"error": "API Key missing"}

        markers_context = json.dumps(self.markers_data['competencies'], indent=2)
        
        lang_instruction = "Translate the 'reasoning' and 'evidence' (if possible/relevant) into Arabic. Keep Marker IDs (e.g., 3.1) as is." if language == "العربية" else "Output in English."

    def analyze_markers(self, content, is_audio=False, language="English"):
        markers_context = json.dumps(self.markers_data, ensure_ascii=False)
        lang_instruction = "Provide ALL text output in Arabic including evidence, reasoning, and auditor notes." if language == "العربية" else "Provide ALL text output in English."
        
        prompt = f"""
You are an EXPERT ICF ASSESSOR conducting a MASTER CERTIFIED COACH (MCC) level audit.

PERSONA & TONE:
- Professional, clinical, and precise
- Avoid cheerleading language (e.g., "Good job!", "Well done!")
- Use professional coaching terminology: "Ontological shift", "Partnering", "Evoking Awareness", "Co-creating", "Client's Agenda"
- Be a RUTHLESS auditor - identify gaps with surgical precision

SCORING PHILOSOPHY:
- Baseline: 6/10 (Competent)
- 10/10 is PERFECTION (rare)
- Award points ONLY for explicit, verifiable evidence
- Deduct points for violations or missed opportunities
- Each competency score reflects marker coverage (Pass = contribute, Fail = reduce score)

{lang_instruction}

MARKERS REFERENCE:
{markers_context}

REQUIRED JSON OUTPUT STRUCTURE:
{{
    "talk_ratio": "Client: XX% / Coach: YY%",
    "silence_count": <integer>,
    "overall_score": <float 1-10>,
    "competencies": {{
        "C1": {{
            "name": "Demonstrates Ethical Practice",
            "score": <float 1-10>,
            "markers": [
                {{
                    "id": "1.1",
                    "status": "Pass" or "Fail",
                    "evidence": "Direct quote with [timestamp] if available",
                    "auditor_note": "Clinical critique: What was observed or what was missing"
                }}
            ]
        }},
        "C2": {{ ... }},
        ... (all 8 competencies C1-C8)
    }}
}}

ANALYSIS INSTRUCTIONS:
1. Estimate talk_ratio based on dialogue distribution
2. Count silence moments (pauses > 3 seconds)
3. For each marker:
   - Status = "Pass" if evidence clearly demonstrates the behavior
   - Status = "Fail" if not observed or insufficient
   - Evidence = Exact quote with context
   - Auditor Note = Professional critique explaining your decision
4. Calculate competency scores based on marker pass/fail ratio and quality
5. Calculate overall_score as weighted average of all competencies

Be strict but fair. This is MCC-level assessment.
"""
        
        try:
            if is_audio:
                response = self.model_pro.generate_content([prompt, content], generation_config={"response_mime_type": "application/json"})
            else:
                response = self.model_flash.generate_content(prompt + f"\n\nCOACHING SESSION TRANSCRIPT:\n{content}", generation_config={"response_mime_type": "application/json"})
                
            # Clean up JSON
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            
            result = json.loads(text)
            
            # Ensure overall_score exists
            if 'overall_score' not in result:
                # Calculate from competencies
                comp_scores = [comp.get('score', 6) for comp in result.get('competencies', {}).values()]
                result['overall_score'] = sum(comp_scores) / len(comp_scores) if comp_scores else 6.0
            
            return result
        except Exception as e:
            return {"error": str(e)}

    def upload_audio(self, audio_file_path, mime_type):
        try:
            myfile = genai.upload_file(audio_file_path, mime_type=mime_type)
            while myfile.state.name == "PROCESSING":
                time.sleep(1)
                myfile = genai.get_file(myfile.name)
            if myfile.state.name == "FAILED":
                raise ValueError("Audio processing failed.")
            return myfile
        except Exception as e:
            raise e

    def generate_quiz_question(self, language="English"):
        comps = self.markers_data['competencies']
        comp = random.choice(comps)
        if not comp['markers']: return None
        marker = random.choice(comp['markers'])
        
        lang_instruction = "Translate the question, options, and explanation into Arabic." if language == "العربية" else "Ensure the output is in English."
        
        prompt = f"""
        Generate a multiple-choice question about ICF PCC Marker {marker['id']}: "{marker['text']}".
        Type: Definition check.
        Language: {language}
        
        {lang_instruction}
        
        Output Format:
        Return ONLY a raw JSON object (no markdown formatting like ```json ... ```):
        {{
            "question": "The question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "The correct option text (must be exactly one of the options)",
            "explanation": "Why it is correct"
        }}
        """
        
        for attempt in range(3):
            try:
                response = self.model_flash.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                text = response.text.strip()
                # Remove markdown if present
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                
                data = json.loads(text)
                
                # Basic validation
                if "question" in data and "options" in data and "correct_answer" in data:
                    return data
            except Exception as e:
                print(f"Quiz Generation Error (Attempt {attempt+1}): {e}")
                last_error = e
                time.sleep(1)
        
        # Fallback if all retries fail
        error_msg = f"Error generating question: {str(last_error)}" if language == "English" else f"حدث خطأ في توليد السؤال: {str(last_error)}"
        return {
            "question": error_msg,
            "options": ["Error"],
            "correct_answer": "Error",
            "explanation": "Please check API Key and Model availability."
        }

class SimulationEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_scenario(self, language="English"):
        lang_instruction = "Generate the scenario in Arabic." if language == "العربية" else "Generate in English."
        prompt = f"""
        Generate a short, challenging coaching scenario (2-3 sentences).
        Describe the client's current state and what they just said to the coach.
        {lang_instruction}
        Output JSON: {{"scenario_text": "..."}}
        """
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)['scenario_text']
        except:
            return "Error generating scenario."

    def grade_response(self, scenario, user_response, language="English"):
        lang_instruction = "Provide feedback in Arabic." if language == "العربية" else "Provide feedback in English."
        prompt = f"""
        Role: PCC Assessor.
        Scenario: {scenario}
        Coach's Response: "{user_response}"
        
        Task: Evaluate the Coach's response.
        1. Identify which PCC Marker it demonstrates.
        2. Give a rating.
        3. Provide brief feedback.
        
        {lang_instruction}
        
        Output JSON:
        {{
            "rating": "Strong" | "Acceptable" | "Needs Improvement",
            "marker_demonstrated": "Marker ID or None",
            "feedback": "..."
        }}
        """
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            return {"rating": "Error", "feedback": str(e)}
