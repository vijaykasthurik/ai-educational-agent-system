from ollama_service import ask_llm
import json
import re

class GeneratorAgent:

    def generate(self, grade, topic, feedback=None):
        # Grade-level language guidance
        grade_guidance = {
            1: "Use very simple words (1-2 syllables). Short sentences (5-8 words). Use fun examples.",
            2: "Use simple words. Short sentences (6-10 words). Relate to everyday objects.",
            3: "Use familiar vocabulary. Sentences can be slightly longer. Include relatable examples.",
            4: "Use grade-appropriate vocabulary. Clear explanations. Real-world connections.",
            5: "Slightly more advanced vocabulary. Can introduce subject-specific terms with definitions.",
            6: "Can use more complex sentence structures. Introduce formal academic language.",
            7: "Academic vocabulary appropriate. Can handle abstract concepts.",
            8: "Advanced academic language. Complex reasoning and examples.",
            9: "High school level vocabulary. Sophisticated explanations.",
            10: "Advanced concepts. Formal academic writing.",
            11: "Pre-college level complexity.",
            12: "College-prep level content."
        }
        
        grade_int = int(grade) if str(grade).isdigit() else 4
        language_guide = grade_guidance.get(grade_int, grade_guidance[4])

        prompt = f"""You are an educational content generator. Generate content for Grade {grade} on "{topic}".

LANGUAGE for Grade {grade}: {language_guide}

CRITICAL: Output ONLY valid JSON. No intro text, no markdown.

Format:
{{
"explanation": "2 short paragraphs explaining the topic.",
"mcqs": [
{{ "question": "Q1", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "A" }},
{{ "question": "Q2", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "B" }},
{{ "question": "Q3", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "C" }}
]
}}
"""

        if feedback:
            prompt += f"\n\nRefinement Request: {feedback}"

        response = ask_llm(prompt)
        return self._parse_response(response)
    
    def _parse_response(self, response):
        """Extract and parse JSON from response with robust repair logic"""
        # Clean up the response
        response = response.strip()
        
        # Remove markdown code blocks
        response = re.sub(r'^```(?:json)?\s*', '', response)
        response = re.sub(r'\s*```$', '', response)
        response = response.strip()
        
        def try_parse(text):
            try:
                parsed = json.loads(text)
                # If we got a string back, it might be double encoded
                if isinstance(parsed, str):
                    try:
                        return json.loads(parsed)
                    except:
                        return parsed # Return the string if it's not JSON
                return parsed
            except json.JSONDecodeError:
                return None

        # 1. Try direct parse
        parsed = try_parse(response)
        if parsed and isinstance(parsed, dict) and "explanation" in parsed:
             return parsed

        # 2. Try partial repair (common issue: missing closing brace/bracket)
        # Try appending } or ]}
        candidates = [response + '}', response + ']}', response + '"}]}', response + ']}}}']
        for cand in candidates:
            parsed = try_parse(cand)
            if parsed and isinstance(parsed, dict): 
                return parsed
        
        # 3. Try to find the valid JSON object within the string
        start_idx = response.find('{')
        if start_idx != -1:
            # Try to substring to the last '}'
            end_idx = response.rfind('}')
            if end_idx != -1 and end_idx > start_idx:
                candidate = response[start_idx:end_idx+1]
                parsed = try_parse(candidate)
                if parsed and isinstance(parsed, dict): return parsed

        # 4. Fallback: Manually check for keys if JSON parsing fails completely
        if "explanation" in response:
            try:
                # Crude extraction using regex as last resort
                explanation = "Content generated but format was complex."
                exp_match = re.search(r'"explanation":\s*"(.*?)(?<!\\)"', response, re.DOTALL)
                if exp_match:
                    explanation = exp_match.group(1)
                
                # Attempt to extract MCQs via regex if JSON parsing failed
                mcqs = []
                try:
                    # Find all MCQ objects
                    mcq_matches = re.finditer(r'\{\s*"question":\s*"(.*?)".*?"options":\s*\[(.*?)\].*?"answer":\s*"(.*?)"\s*\}', response, re.DOTALL)
                    for match in mcq_matches:
                        q_text = match.group(1)
                        opts_text = match.group(2)
                        ans_text = match.group(3)
                        
                        # Clean up options
                        options = [opt.strip().strip('"').strip("'") for opt in opts_text.split(',')]
                        
                        mcqs.append({
                            "question": q_text,
                            "options": options,
                            "answer": ans_text
                        })
                except:
                    pass

                return {
                    "explanation": explanation,
                    "mcqs": mcqs,
                    "partial_parse": True
                }
            except:
                pass

        return {"raw_response": response, "parse_error": True}
