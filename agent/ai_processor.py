from google import genai
import os

class AIProcessor:
    def __init__(self, api_key):
        if not api_key or api_key == "your_gemini_api_key_here":
            self.client = None
            print("Warning: Gemini API Key missing or default. Summaries will be literal.")
            return
        
        self.client = genai.Client(api_key=api_key)

    def summarize_repo(self, name, description):
        if not self.client:
            return description

        prompt = f"""
        You are RepoLumin, an AI expert at summarizing software projects.
        The project is called '{name}'. 
        Original description: {description}
        
        Write a concise, high-signal 1-sentence summary that explains exactly what this project does and why it is useful.
        Do not use buzzwords. Just the facts.
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"AI Summary failed for {name}: {e}")
            return description
