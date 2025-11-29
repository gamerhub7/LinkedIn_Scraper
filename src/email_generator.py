"""
OpenAI Email Generator Module
Generates personalized emails using OpenAI's GPT API
"""

import re
import logging
import json
from typing import Dict, Optional
from openai import OpenAIError, RateLimitError, APIError
from pydantic import BaseModel, Field, ValidationError

from .config import Config, get_openai_client, get_model_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonalizedEmail(BaseModel):
    """Pydantic model for email validation"""
    subject: str = Field(..., description="Email subject line", max_length=100)
    body: str = Field(..., description="Email body content")


import google.generativeai as genai

class EmailGenerator:
    """Generate personalized emails using OpenAI GPT or Gemini"""

    def __init__(self, llm_provider: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the email generator with LLM client"""
        # Determine provider and key
        self.provider = llm_provider or Config.get_provider()
        self.api_key = api_key
        
        if self.provider == 'gemini':
            key = self.api_key or Config.GEMINI_API_KEY
            if not key:
                logger.warning("No Gemini API key provided")
            else:
                genai.configure(api_key=key)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            self.client = None
        else:
            # For OpenAI/Azure
            if self.api_key and self.provider == 'openai':
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            else:
                self.client = get_openai_client()
            self.model = get_model_name()

    def generate_email(self, profile_data: Dict[str, Optional[str]], max_retries: int = 3) -> Dict[str, str]:
        """
        Generate a personalized email based on LinkedIn profile data
        Uses Pydantic for validation and retries on failure

        Args:
            profile_data: Dictionary containing name, title, company, and about information
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary containing subject and body, or error
        """
        for attempt in range(max_retries):
            try:
                # Build the prompt
                prompt = self._create_prompt(profile_data)

                logger.info(f"Generating email for {profile_data.get('name', 'Unknown')}... (attempt {attempt + 1})")

                response_text = ""

                if self.provider == 'gemini':
                    # Gemini Call
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.GenerationConfig(
                            temperature=0.7,
                            response_mime_type="application/json"
                        )
                    )
                    response_text = response.text.strip()
                else:
                    # OpenAI/Azure Call
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert at writing professional, personalized emails. You ONLY respond with valid JSON containing 'subject' and 'body' fields. Never add explanatory text or markdown."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=500,
                        response_format={"type": "json_object"}  # Force JSON mode
                    )
                    response_text = response.choices[0].message.content.strip()

                # Clean any potential markdown artifacts
                response_text = re.sub(r'^```json\s*', '', response_text)
                response_text = re.sub(r'^```\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)
                response_text = response_text.strip()

                # Parse JSON
                parsed_data = json.loads(response_text)

                # Handle case where LLM returns a list instead of a dict
                if isinstance(parsed_data, list):
                    if len(parsed_data) > 0:
                        parsed_data = parsed_data[0]
                    else:
                        parsed_data = {}

                # Validate with Pydantic
                email = PersonalizedEmail(**parsed_data)

                # Convert to dict
                email_data = email.model_dump()

                logger.info("✓ Email generated successfully")
                return email_data

            except json.JSONDecodeError as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: JSON parse error - {str(e)}")

                if attempt == max_retries - 1:
                    return {
                        'subject': None,
                        'body': None,
                        'error': f'Failed to parse valid JSON after {max_retries} attempts'
                    }

            except ValidationError as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: Pydantic validation error - {str(e)}")

                if attempt == max_retries - 1:
                    return {
                        'subject': None,
                        'body': None,
                        'error': f'Failed to validate email schema after {max_retries} attempts'
                    }

            except RateLimitError as e:
                logger.error(f"OpenAI rate limit exceeded: {str(e)}")
                return {
                    'subject': None,
                    'body': None,
                    'error': 'OpenAI rate limit exceeded. Please try again later.'
                }

            except APIError as e:
                logger.error(f"OpenAI API error: {str(e)}")
                return {
                    'subject': None,
                    'body': None,
                    'error': f'OpenAI API error: {str(e)}'
                }

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries}: Unexpected error - {str(e)}")

                if attempt == max_retries - 1:
                    return {
                        'subject': None,
                        'body': None,
                        'error': f'Email generation error: {str(e)}'
                    }

        # This should never be reached
        return {
            'subject': None,
            'body': None,
            'error': 'Unknown error during email generation'
        }

    def _create_prompt(self, profile_data: Dict[str, Optional[str]]) -> str:
        """
        Create a prompt for OpenAI based on profile data

        Args:
            profile_data: Dictionary containing profile information

        Returns:
            Formatted prompt string
        """
        name = profile_data.get('name', 'the person')
        title = profile_data.get('title', 'their current role')
        company = profile_data.get('company', 'their company')
        about = profile_data.get('about', '')

        # Build the prompt with available information
        prompt = f"""Generate a professional and personalized email to reach out to someone on LinkedIn.

Profile Information:
- Name: {name}
- Current Position: {title}
- Company: {company}"""

        if about:
            prompt += f"\n- About: {about}"

        prompt += """

Requirements:
1. Create a compelling subject line (max 60 characters)
2. Write a personalized email body that:
   - References specific details from their profile
   - Sounds genuine and professional
   - Is concise (2-3 paragraphs max)
   - Has a clear purpose or call to action
   - Avoids being overly salesy or generic

CRITICAL: Return ONLY a JSON object with this exact structure:
{"subject": "your subject line", "body": "your email body"}

No markdown, no code blocks, no additional text - just pure JSON."""

        return prompt


def generate_personalized_email(profile_data: Dict[str, Optional[str]], llm_provider: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Convenience function to generate a personalized email

    Args:
        profile_data: Dictionary containing profile information
        llm_provider: LLM provider (optional)
        api_key: API key (optional)

    Returns:
        Dictionary containing subject and body
    """
    generator = EmailGenerator(llm_provider=llm_provider, api_key=api_key)
    return generator.generate_email(profile_data)
