from google import genai
import os

class AIProcessor:
    def __init__(self, api_key):
        if not api_key or api_key in ["your_gemini_api_key_here", ""]:
            self.client = None
            print("[bold red]Error: Invalid Gemini API Key.[/bold red] Please update your .env file.")
            return
        
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            self.client = None
            print(f"Failed to initialize Gemini Client: {e}")

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
