import google.generativeai as genai
import os

class AIProcessor:
    def __init__(self, api_key):
        if not api_key:
            self.model = None
            print("Warning: Gemini API Key missing. Summaries will be literal.")
            return
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def summarize_repo(self, name, description):
        if not self.model:
            return description

        prompt = f"""
        You are RepoLumin, an AI expert at summarizing software projects.
        The project is called '{name}'. 
        Original description: {description}
        
        Write a concise, high-signal 1-sentence summary that explains exactly what this project does and why it is useful.
        Do not use buzzwords. Just the facts.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI Summary failed for {name}: {e}")
            return description
