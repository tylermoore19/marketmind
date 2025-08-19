import os
from google import genai
from utils.helpers import extract_json_array
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool

class GeminiClientError(Exception):
    """Custom exception for GeminiClient errors."""
    pass

class GeminiClient:
    """Client for interacting with the Gemini API."""

    def __init__(self):
        self.api_key = os.environ.get('GENAI_API_KEY')
        self.client = genai.Client(api_key=self.api_key)
        self.model = 'gemini-2.5-pro'

    def _generate_content(self, instructions: str, system_instructions: list[str]):
        """Internal helper to call Gemini API with error handling"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=instructions,
                config=GenerateContentConfig(
                    tools=[Tool(google_search=GoogleSearch())],
                    system_instruction=system_instructions,
                    temperature=0
                )
            )
            return extract_json_array(response.text)
        except Exception as e:
            raise GeminiClientError(f"Gemini API call failed: {e}")

    def get_top_sport_picks(self, date: str):
        """Fetch top sports picks for a given date."""
        try:
            # Get the absolute path to the instructions file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            instructions_path = os.path.join(script_dir, '../', 'instructions', 'top_value_sport_games_prompt.md')

            with open(instructions_path, 'r') as f:
                instructions = f.read()

            # Call the helper
            system_instructions = [
                "You are a sports betting expert.",
                f"Your mission is to find the top 5 value bets for games on {date}.",
            ]

            return self._generate_content(instructions, system_instructions)
        except Exception as e:
            raise GeminiClientError(f"Failed to fetch top sports picks - {e}")