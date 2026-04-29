import os
import json
import logging
from typing import Optional, List, Dict
import openai
from openai import OpenAI
import google.generativeai as genai
import anthropic
from mistralai.client import MistralClient

logger = logging.getLogger("WalleAgent.LLM")

class LLMProvider:
    def __init__(self):
        self.provider_name = os.getenv("LLM_PROVIDER", "openai").lower()
        self.default_model = os.getenv("DEFAULT_MODEL")
        self.offline_fallback = os.getenv("OFFLINE_FALLBACK", "true").lower() == "true"
        
        # Initialize clients
        self.openai_client = self._init_openai()
        self.gemini_client = self._init_gemini()
        self.anthropic_client = self._init_anthropic()
        self.mistral_client = self._init_mistral()
        self.groq_client = self._init_groq()
        self.openrouter_client = self._init_openrouter()

    def _init_openai(self):
        key = os.getenv("OPENAI_API_KEY")
        if key and "your_" not in key:
            return OpenAI(api_key=key)
        return None

    def _init_gemini(self):
        key = os.getenv("GEMINI_API_KEY")
        if key and "your_" not in key:
            genai.configure(api_key=key)
            return True
        return None

    def _init_anthropic(self):
        key = os.getenv("ANTHROPIC_API_KEY")
        if key and "your_" not in key:
            return anthropic.Anthropic(api_key=key)
        return None

    def _init_mistral(self):
        key = os.getenv("MISTRAL_API_KEY")
        if key and "your_" not in key:
            return MistralClient(api_key=key)
        return None

    def _init_groq(self):
        key = os.getenv("GROQ_API_KEY")
        if key and "your_" not in key:
            return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        return None

    def _init_openrouter(self):
        key = os.getenv("OPENROUTER_API_KEY")
        if key and "your_" not in key:
            return OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")
        return None

    def analyze(self, context_data: Dict) -> Dict:
        try:
            if self.provider_name == "openai" and self.openai_client:
                return self._call_openai(context_data)
            elif self.provider_name == "gemini" and self.gemini_client:
                return self._call_gemini(context_data)
            elif self.provider_name == "anthropic" and self.anthropic_client:
                return self._call_anthropic(context_data)
            elif self.provider_name == "mistral" and self.mistral_client:
                return self._call_mistral(context_data)
            elif self.provider_name == "groq" and self.groq_client:
                return self._call_openai_compatible(self.groq_client, context_data, "Groq")
            elif self.provider_name == "openrouter" and self.openrouter_client:
                return self._call_openai_compatible(self.openrouter_client, context_data, "OpenRouter")
            
            # If no provider matched or initialized
            return self._fallback(context_data, f"Provider '{self.provider_name}' not configured or missing API key.")
        
        except Exception as e:
            logger.error(f"LLM Error ({self.provider_name}): {str(e)}")
            if self.offline_fallback:
                return self._fallback(context_data, str(e))
            raise e

    def _call_openai(self, context_data: Dict) -> Dict:
        model = self.default_model or "gpt-4o-mini"
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful browser assistant. Always return valid JSON."},
                {"role": "user", "content": self._build_prompt(context_data)}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)

    def _call_openai_compatible(self, client: OpenAI, context_data: Dict, name: str) -> Dict:
        model = self.default_model or ("llama3-8b-8192" if name == "Groq" else "google/gemini-2.0-flash-001")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful browser assistant. Always return valid JSON."},
                {"role": "user", "content": self._build_prompt(context_data)}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)

    def _call_gemini(self, context_data: Dict) -> Dict:
        model_name = self.default_model or "gemini-2.0-flash"
        model = genai.GenerativeModel(model_name)
        prompt = self._build_prompt(context_data) + "\nReturn ONLY valid JSON."
        response = model.generate_content(prompt)
        # Gemini sometimes adds markdown code blocks
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    def _call_anthropic(self, context_data: Dict) -> Dict:
        model = self.default_model or "claude-3-5-sonnet-20240620"
        prompt = self._build_prompt(context_data)
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            system="You are a helpful browser assistant. Always return valid JSON.",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.content[0].text)

    def _call_mistral(self, context_data: Dict) -> Dict:
        from mistralai.models.chat_completion import ChatMessage
        model = self.default_model or "mistral-tiny"
        messages = [
            ChatMessage(role="user", content=self._build_prompt(context_data) + "\nReturn valid JSON.")
        ]
        response = self.mistral_client.chat(model=model, messages=messages)
        return json.loads(response.choices[0].message.content)

    def _build_prompt(self, context: Dict) -> str:
        return f"""
        Analyze this page:
        URL: {context.get('url')}
        Title: {context.get('title')}
        Text: {context.get('text', '')[:1500]}
        Elements: Forms({len(context.get('forms', []))}), Buttons({len(context.get('buttons', []))})
        
        Return JSON:
        {{
          "summary": "...",
          "suggested_actions": ["..."],
          "safety_note": "..."
        }}
        """

    def _fallback(self, context: Dict, error: str) -> Dict:
        return {
            "summary": f"Offline Analysis: {context.get('title')}. Read {len(context.get('text', ''))} chars.",
            "suggested_actions": [
                "Review visible elements",
                "Try refreshing the page"
            ],
            "safety_note": f"⚠️ Fallback mode active. Reason: {error[:100]}"
        }
