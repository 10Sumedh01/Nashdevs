# aiIntegration.py
import requests

class AIHelper:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_doctor_guidance(self, prompt):
        # In a real integration, you would send a request to the Gemini API endpoint.
        # For example:
        # response = requests.post(
        #     "https://api.gemini.example.com/generate",
        #     json={"prompt": prompt},
        #     headers={"Authorization": f"Bearer {self.api_key}"}
        # )
        # return response.json().get("text", "")
        return "Stay alert, every decision counts. Trust your instincts."
