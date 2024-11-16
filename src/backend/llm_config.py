from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing import Union, Optional
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

class LLMProvider:
    def __init__(self):
        self.preferred_llm = os.getenv('PREFERRED_LLM', 'claude')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')

        # Initialize LLM instances
        self.claude = None
        self.openai = None

        self._initialize_llms()

    def _initialize_llms(self):
        """Initialize the specified LLM(s)"""
        if self.preferred_llm in ['claude', 'both'] and self.anthropic_key:
            self.claude = ChatAnthropic(
                model="claude-3-opus-20240229",
                anthropic_api_key=self.anthropic_key,
                temperature=0.7
            )

        if self.preferred_llm in ['openai', 'both'] and self.openai_key:
            self.openai = ChatOpenAI(
                model="gpt-4",
                openai_api_key=self.openai_key,
                temperature=0.7
            )

    def get_primary_llm(self):
        """Get the preferred LLM instance"""
        if self.preferred_llm == 'claude' and self.claude:
            return self.claude
        elif self.preferred_llm == 'openai' and self.openai:
            return self.openai
        elif self.claude:
            return self.claude
        elif self.openai:
            return self.openai
        else:
            raise ValueError("No LLM available. Please configure either Claude or OpenAI.")

    def get_secondary_llm(self):
        """Get the secondary LLM for validation or fallback"""
        if self.preferred_llm == 'claude' and self.openai:
            return self.openai
        elif self.preferred_llm == 'openai' and self.claude:
            return self.claude
        return None
