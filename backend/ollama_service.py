import ollama

def ask_llm(prompt, temperature=0.3):
    """
    Call Ollama LLM with optimized settings for educational content generation.
    
    Args:
        prompt: The prompt to send to the LLM
        temperature: Controls randomness (0.1-0.4 recommended for structured output)
    """
    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "system",
                "content": "You are a precise educational content assistant. Always output valid JSON only, with no additional text, explanations, or markdown formatting. Start your response with { and end with }."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": temperature,
            "top_p": 0.9,
            "num_predict": 2048
        }
    )

    return response["message"]["content"]
