"""
AI Parser module for processing natural language commands using Ollama
Extracts company name and job type from user input
"""

import json
import logging
import requests
from typing import Dict, Optional, Any

from app.config import Config

logger = logging.getLogger(__name__)


class AIParser:
    """
    AI-based command parser using Ollama local LLM
    Extracts structured information from natural language input
    """

    def __init__(self):
        """Initialize the AI parser with Ollama configuration"""
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        self.timeout = 30  # seconds

    def extract_company_and_job(self, user_input: str) -> Dict[str, str]:
        """
        Extract company name and job type from natural language input

        Args:
            user_input: Natural language text describing the document context

        Returns:
            Dict containing 'company' and 'job_type' keys
        """
        try:
            response = self._call_ollama(user_input)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return self._get_fallback_response(user_input)

    def _call_ollama(self, prompt: str) -> str:
        """
        Make API call to Ollama

        Args:
            prompt: Input text to process

        Returns:
            Raw response from Ollama
        """
        system_prompt = """You are an AI assistant specialized in parsing Indonesian legal document instructions.
Extract the company name and job type from the user's input and respond only in JSON format.

Examples:
Input: "Ini untuk PT Jaminan Nasional Indonesia, pekerjaan pengurusan izin PPIU."
Output: {"company": "PT Jaminan Nasional Indonesia", "job_type": "pengurusan izin PPIU"}

Input: "Dokumen PT Makmur Sentosa untuk perpanjangan SIUP"
Output: {"company": "PT Makmur Sentosa", "job_type": "perpanjangan SIUP"}

Input: "File untuk PT Cahaya Abadi, pengurusan NPWP"
Output: {"company": "PT Cahaya Abadi", "job_type": "pengurusan NPWP"}

Rules:
1. Always include "PT" in company names when present
2. Extract job type as descriptive as possible
3. Respond ONLY with valid JSON, no explanations
4. If you cannot extract information, use "Unknown" for both fields"""

        full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent output
                        "max_tokens": 200
                    }
                },
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return data.get("response", "").strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode Ollama response: {str(e)}")
            raise

    def _parse_response(self, response: str) -> Dict[str, str]:
        """
        Parse the AI response and extract JSON data

        Args:
            response: Raw response from Ollama

        Returns:
            Parsed dictionary with company and job_type
        """
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)

            # Validate required fields
            if 'company' not in data or 'job_type' not in data:
                raise ValueError("Missing required fields in JSON response")

            return {
                'company': str(data['company']).strip(),
                'job_type': str(data['job_type']).strip()
            }

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {response}. Error: {str(e)}")
            raise

    def _get_fallback_response(self, user_input: str) -> Dict[str, str]:
        """
        Provide fallback response when AI parsing fails
        Uses simple pattern matching as fallback

        Args:
            user_input: Original user input

        Returns:
            Basic response with parsed information
        """
        logger.warning("Using fallback parsing due to AI failure")

        # Simple pattern matching for common patterns
        company = "Unknown"
        job_type = "Unknown"

        # Try to extract company name with "PT"
        import re
        pt_patterns = [
            r'(PT\s+[\w\s]+?),',  # PT Company Name, ...
            r'(PT\s+[\w\s]+?)\s+untuk',  # PT Company Name untuk ...
            r'(PT\s+[\w\s]+?)\s+dari',  # PT Company Name dari ...
        ]

        for pattern in pt_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                break

        # Try to extract job type
        job_patterns = [
            r'(?:pekerjaan|pengurusan|perpanjangan)\s+([^.!,\n]+)',
            r'untuk\s+([^.!,\n]+)',
            r'file\s+.*?\s+([^.!,\n]+)',
        ]

        for pattern in job_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                job_type = match.group(1).strip()
                break

        return {
            'company': company,
            'job_type': job_type
        }

    def test_connection(self) -> bool:
        """
        Test connection to Ollama

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])

            # Check if our model is available
            model_available = any(model.get('name') == self.model for model in models)

            if not model_available:
                logger.warning(f"Model {self.model} not found. Available models: {[m.get('name') for m in models]}")
                return False

            logger.info(f"Successfully connected to Ollama with model: {self.model}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {str(e)}")
            return False

    def get_available_models(self) -> list:
        """
        Get list of available models from Ollama

        Returns:
            List of available model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])
            return [model.get('name') for model in models]
        except Exception as e:
            logger.error(f"Failed to get available models: {str(e)}")
            return []


# Example usage and testing
if __name__ == "__main__":
    def test_parser():
        """Test the AI parser with sample inputs"""
        parser = AIParser()

        # Test connection
        if not parser.test_connection():
            print("Failed to connect to Ollama. Please make sure Ollama is running.")
            return

        # Test inputs
        test_inputs = [
            "Ini untuk PT Jaminan Nasional Indonesia, pekerjaan pengurusan izin PPIU.",
            "Dokumen PT Makmur Sentosa untuk perpanjangan SIUP",
            "File untuk PT Cahaya Abadi, pengurusan NPWP",
        ]

        for test_input in test_inputs:
            print(f"\nInput: {test_input}")
            try:
                result = parser.extract_company_and_job(test_input)
                print(f"Output: {result}")
            except Exception as e:
                print(f"Error: {str(e)}")

    test_parser()