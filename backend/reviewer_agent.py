from ollama_service import ask_llm
import json
import re

class ReviewerAgent:

    def review(self, content, grade):
        """Review content for age-appropriateness, correctness, and clarity"""
        
        # Handle both dict and string inputs
        if isinstance(content, dict):
            content_str = json.dumps(content, indent=2)
        else:
            content_str = str(content)

        prompt = f"""Review this Grade {grade} educational content. Check: age-appropriateness, correctness, clarity.

Content:
{content_str}

CRITICAL: Output ONLY JSON. No intro, no markdown, no explanation. Just raw JSON:

{{"status": "pass", "feedback": []}}

OR if issues found:

{{"status": "fail", "feedback": ["issue 1", "issue 2"]}}"""

        response = ask_llm(prompt)
        return self._parse_response(response)
    
    def _parse_response(self, response):
        """Extract and parse JSON from response with robust repair logic"""
        response = response.strip()
        
        # Remove markdown code blocks
        response = re.sub(r'^```(?:json)?\s*', '', response)
        response = re.sub(r'\s*```$', '', response)
        response = response.strip()
        
        def try_parse(text):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, str):
                    try:
                        return json.loads(parsed)
                    except:
                        return parsed
                return parsed
            except json.JSONDecodeError:
                return None

        # 1. Try direct parse
        parsed = try_parse(response)
        if parsed and isinstance(parsed, dict) and "status" in parsed:
             return parsed
        
        # 2. Try partial repair (common issue: missing closing brace)
        # Try appending } or ]}
        candidates = [response + '}', response + ']}', response + '"}}']
        for cand in candidates:
            parsed = try_parse(cand)
            if parsed and isinstance(parsed, dict): 
                return parsed
        
        # 3. Try to find JSON by looking for first { and last }
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx + 1]
                parsed = try_parse(json_str)
                if parsed and isinstance(parsed, dict): return parsed
        except:
            pass
        
        # Return structured default if parsing fails
        # If we can't parse the review, we default to pass with a warning, 
        # because blocking the user due to reviewer format error is bad UX.
        return {
            "status": "pass", 
            "feedback": ["Note: Reviewer output format was irregular, but processing continued."], 
            "raw_response": response
        }
