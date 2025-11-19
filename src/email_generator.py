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
    
    subject: str = Field(..., description="Email subject line", max_length=100)
    body: str = Field(..., description="Email body content")


class EmailGenerator:
   

    def __init__(self):
        
        self.client = get_openai_client()
        self.model = get_model_name()

    def generate_email(self, profile_data: Dict[str, Optional[str]], max_retries: int = 3) -> Dict[str, str]:
        
        for attempt in range(max_retries):
            try:
              
                prompt = self._create_prompt(profile_data)

                logger.info(f"Generating email for {profile_data.get('name', 'Unknown')}... (attempt {attempt + 1})")

               
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
                    response_format={"type": "json_object"}  
                )

                
                response_text = response.choices[0].message.content.strip()

                
                response_text = re.sub(r'^```json\s*', '', response_text)
                response_text = re.sub(r'^```\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)
                response_text = response_text.strip()

                
                parsed_data = json.loads(response_text)

               
                email = PersonalizedEmail(**parsed_data)

               
                email_data = email.model_dump()

                logger.info(" Email generated successfully")
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

      
        return {
            'subject': None,
            'body': None,
            'error': 'Unknown error during email generation'
        }

    def _create_prompt(self, profile_data: Dict[str, Optional[str]]) -> str:
        
        name = profile_data.get('name', 'the person')
        title = profile_data.get('title', 'their current role')
        company = profile_data.get('company', 'their company')
        about = profile_data.get('about', '')

        
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


def generate_personalized_email(profile_data: Dict[str, Optional[str]]) -> Dict[str, str]:
    generator = EmailGenerator()
    return generator.generate_email(profile_data)
