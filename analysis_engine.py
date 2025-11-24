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
        """
        Stage 2: PCC Marker Detection and Compliance Assessment
        """
        if not self.api_key:
            return {"error": "API Key missing"}

        markers_context = json.dumps(self.markers_data, ensure_ascii=False)
        lang_instruction = "Provide ALL text output in Arabic including evidence, reasoning, and feedback." if language == "العربية" else "Provide ALL text output in English."
        
        prompt = f"""
You are an EXPERT ICF PCC ASSESSOR conducting a PROFESSIONAL CERTIFIED COACH (PCC) level audit.
Your evaluation Bible is the "ICF PCC Markers 2021" document.

CRITICAL: This is PCC Level (Level 2), NOT MCC (Level 3).
- Focus on OBSERVABLE BEHAVIORS (Markers), not artistry or mastery
- Evaluate based on PRESENCE or ABSENCE of specific marker behaviors
- Use clear, evidence-based assessment

PERSONA & TONE:
- Professional, objective, and evidence-based
- Avoid subjective language like "masterful" or "transformational"
- Use PCC terminology: "Observable behavior", "Marker demonstrated", "Evidence of partnering"
- Be precise and clinical in your assessment

PCC SCORING PHILOSOPHY:
- Count MARKERS, not subjective quality
- Each marker is either "Observed" or "Not Observed"
- Compliance % = (Markers Observed / Total Markers) × 100
- PCC Pass Threshold: Typically 70-80% marker compliance
- Focus on WHAT WAS DONE, not how beautifully it was done

{lang_instruction}

MARKERS REFERENCE (8 Competencies → 37 Markers):
{markers_context}

REQUIRED JSON OUTPUT STRUCTURE:
{{
    "talk_ratio": "Client: XX% / Coach: YY%",
    "silence_count": <integer>,
    "markers_observed": <integer count of markers with status "Observed">,
    "total_markers": 37,
    "compliance_percentage": <float 0-100>,
    "overall_pcc_result": "Pass" or "Fail",
    "competencies": {{
        "C1": {{
            "name": "Demonstrates Ethical Practice",
            "status": "Pass" or "Fail",
            "feedback": "Brief assessment of ethical practice"
        }},
        "C2": {{
            "name": "Embodies a Coaching Mindset",
            "status": "Pass" or "Fail",
            "feedback": "Assessment based on cross-cutting markers",
            "mapped_markers": ["4.1", "4.3", "4.4", "5.1", "5.2", "5.3", "5.4", "6.1", "6.5", "7.1", "7.5"]
        }},
        "C3": {{
            "name": "Establishes and Maintains Agreements",
            "markers": [
                {{
                    "id": "3.1",
                    "behavior": "Partners with client to identify or reconfirm topic",
                    "status": "Observed" or "Not Observed",
                    "evidence": "Direct quote from session with [timestamp] if available",
                    "feedback": "Specific observation about this marker"
                }},
                {{
                    "id": "3.2",
                    "behavior": "Partners with client to define measures of success",
                    "status": "Observed" or "Not Observed",
                    "evidence": "Direct quote or 'No evidence found'",
                    "feedback": "Specific observation"
                }}
                // Continue for all markers in C3 (3.1-3.4)
            ]
        }},
        "C4": {{
            "name": "Cultivates Trust and Safety",
            "markers": [
                // All markers 4.1-4.4
            ]
        }},
        "C5": {{
            "name": "Maintains Presence",
            "markers": [
                // All markers 5.1-5.5
            ]
        }},
        "C6": {{
            "name": "Listens Actively",
            "markers": [
                // All markers 6.1-6.7
            ]
        }},
        "C7": {{
            "name": "Evokes Awareness",
            "markers": [
                // All markers 7.1-7.8
            ]
        }},
        "C8": {{
            "name": "Facilitates Client Growth",
            "markers": [
                // All markers 8.1-8.9
            ]
        }}
    }}
}}

ANALYSIS INSTRUCTIONS:
1. Estimate talk_ratio based on dialogue distribution
2. Count silence moments (pauses > 3 seconds)
3. For EACH of the 37 markers:
   - Status = "Observed" if you find clear evidence of the behavior
   - Status = "Not Observed" if behavior is absent or insufficient
   - Evidence = Exact quote with context (or "No evidence found")
   - Feedback = Brief note explaining your assessment
4. Count total markers observed
5. Calculate compliance_percentage = (markers_observed / 37) × 100
6. Determine overall_pcc_result:
   - "Pass" if compliance_percentage >= 75%
   - "Fail" if compliance_percentage < 75%

REMEMBER: This is PCC Level. Focus on observable behaviors, not coaching artistry.
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
            
            # VALIDATION: Ensure all 37 markers are present
            expected_markers = {
                'C3': 4,  # 3.1-3.4
                'C4': 4,  # 4.1-4.4
                'C5': 5,  # 5.1-5.5
                'C6': 7,  # 6.1-6.7
                'C7': 8,  # 7.1-7.8
                'C8': 9   # 8.1-8.9
            }
            
            total_expected = sum(expected_markers.values())  # 37 markers
            missing_markers = []
            
            for comp_id, expected_count in expected_markers.items():
                comp_data = result.get('competencies', {}).get(comp_id, {})
                markers_list = comp_data.get('markers', [])
                actual_count = len(markers_list)
                
                if actual_count < expected_count:
                    missing_count = expected_count - actual_count
                    missing_markers.append(f"{comp_id}: {missing_count} markers missing")
            
            # Add validation warning to result if markers are missing
            if missing_markers:
                result['validation_warning'] = {
                    'status': 'INCOMPLETE',
                    'message': f'Analysis incomplete: {", ".join(missing_markers)}',
                    'missing_markers': missing_markers
                }
            else:
                result['validation_warning'] = {
                    'status': 'COMPLETE',
                    'message': 'All 37 markers evaluated'
                }
            
            # Ensure required fields exist
            if 'markers_observed' not in result:
                # Count from competencies
                count = 0
                for comp_id, comp_data in result.get('competencies', {}).items():
                    if 'markers' in comp_data:
                        count += sum(1 for m in comp_data['markers'] if m.get('status') == 'Observed')
                result['markers_observed'] = count
            
            if 'compliance_percentage' not in result:
                result['compliance_percentage'] = (result.get('markers_observed', 0) / 37) * 100
            
            if 'overall_pcc_result' not in result:
                result['overall_pcc_result'] = "Pass" if result.get('compliance_percentage', 0) >= 75 else "Fail"
            
            # Add overall_score for backward compatibility (convert from compliance %)
            result['overall_score'] = (result.get('compliance_percentage', 0) / 10)
            
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
