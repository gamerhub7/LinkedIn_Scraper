import re
import json
import logging
from typing import Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError

from .config import Config, get_openai_client, get_model_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInProfile(BaseModel):
    name: Optional[str] = Field(None, description="Person's full name")
    title: Optional[str] = Field(None, description="Current job title/position")
    company: Optional[str] = Field(None, description="Current company/organization")
    about: Optional[str] = Field(None, description="About section content")


class LinkedInScraper:
   

    def __init__(self, headless: bool = True):
       
        self.headless = headless
        self.client = get_openai_client()
        self.model = get_model_name()

    def scrape_profile(self, url: str) -> Dict[str, Optional[str]]:
       
        try:
            
            logger.info(f"Fetching LinkedIn profile: {url}")
            html_content = self._fetch_profile_html(url)

            if not html_content:
                return {
                    'name': None,
                    'title': None,
                    'company': None,
                    'about': None,
                    'url': url,
                    'error': 'Failed to fetch profile HTML'
                }

           
            logger.info("Cleaning HTML content...")
            cleaned_html = self._clean_html(html_content)

            
            logger.info("Extracting profile information using LLM...")
            profile_data = self._extract_with_llm(cleaned_html, url)

            return profile_data

        except Exception as e:
            logger.error(f"Error scraping profile: {str(e)}")
            return {
                'name': None,
                'title': None,
                'company': None,
                'about': None,
                'url': url,
                'error': f'Scraping error: {str(e)}'
            }

    def _login_to_linkedin(self, page):
       
        try:
            if not Config.LINKEDIN_EMAIL or not Config.LINKEDIN_PASSWORD:
                logger.info("No LinkedIn credentials provided, skipping login")
                return False

            logger.info("Logging in to LinkedIn...")

           
            page.goto('https://www.linkedin.com/checkpoint/rm/sign-in-another-account', wait_until='networkidle')
            page.wait_for_timeout(2000)

            
            logger.info("Entering credentials...")
            page.fill('input[id="username"]', Config.LINKEDIN_EMAIL)
            page.wait_for_timeout(500)

            
            page.fill('input[id="password"]', Config.LINKEDIN_PASSWORD)
            page.wait_for_timeout(500)

            
            page.click('button[aria-label="Sign in"]')
            logger.info("Clicked sign in button, waiting for login...")

           
            page.wait_for_timeout(5000)

           
            current_url = page.url
            if 'feed' in current_url or 'checkpoint' not in current_url:
                logger.info("[OK] Successfully logged in to LinkedIn")
                return True
            else:
                logger.warning("Login may have failed - unexpected URL: " + current_url)
                return False

        except Exception as e:
            logger.error(f"Error during LinkedIn login: {str(e)}")
            return False

    def _expand_see_more_sections(self, page):
        
        try:
            logger.info("Looking for 'see more' buttons to expand sections...")

           
            see_more_selectors = [
                'button[aria-expanded="false"]:has-text("see more")',
                'button[aria-expanded="false"]:has-text("See more")',
                'button[aria-expanded="false"]:has-text("…see more")',
                '[role="button"][aria-expanded="false"]:has-text("see more")',
                '[role="button"][aria-expanded="false"]:has-text("…see more")'
            ]

            clicked_count = 0

            for selector in see_more_selectors:
                try:
                   
                    buttons = page.locator(selector).all()

                    for button in buttons:
                        try:
                            
                            if button.is_visible():
                                logger.info(f"Clicking 'see more' button...")
                                button.click()
                                clicked_count += 1
                                
                                page.wait_for_timeout(1000)
                        except Exception as e:
                            
                            logger.debug(f"Could not click button: {str(e)}")
                            continue

                except Exception as e:
                    logger.debug(f"No buttons found for selector '{selector}': {str(e)}")
                    continue

            if clicked_count > 0:
                logger.info(f"[OK] Clicked {clicked_count} 'see more' button(s)")
               
                page.wait_for_timeout(2000)
            else:
                logger.info("No 'see more' buttons found (sections may already be expanded)")

        except Exception as e:
            logger.warning(f"Error expanding sections: {str(e)}")
          
    def _fetch_profile_html(self, url: str) -> Optional[str]:
        
        try:
            with sync_playwright() as p:
                
                login_method = Config.LOGIN_METHOD

                logger.info(f"Login method: {login_method}")

               
                if login_method == 'chrome_profile' and Config.CHROME_USER_DATA_DIR:
                    logger.info(f"Using Chrome profile: {Config.CHROME_USER_DATA_DIR}")

                 
                    chrome_path = Config.CHROME_USER_DATA_DIR.strip('"').strip("'")

                   
                    context = p.chromium.launch_persistent_context(
                        chrome_path,
                        headless=self.headless,
                        channel='chrome',
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        viewport={'width': 1920, 'height': 1080}
                    )

                  
                    page = context.new_page()

                
                elif login_method == 'credentials':
                    logger.info("Using LinkedIn credentials for login")

                  
                    browser = p.chromium.launch(headless=self.headless)

                    
                    context = browser.new_context(
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        viewport={'width': 1920, 'height': 1080}
                    )

                    
                    page = context.new_page()

                  
                    self._login_to_linkedin(page)

                
                else:
                    logger.warning("No login method configured - scraping may fail for private profiles")

                    
                    browser = p.chromium.launch(headless=self.headless)

                    
                    context = browser.new_context(
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        viewport={'width': 1920, 'height': 1080}
                    )

                   
                    page = context.new_page()

               
                logger.info(f"Navigating to profile: {url}")
                page.goto(url, wait_until='domcontentloaded', timeout=Config.PAGE_LOAD_TIMEOUT * 1000)

               
                page.wait_for_timeout(5000)

               
                self._expand_see_more_sections(page)

              
                html_content = page.content()

               
                context.close()

                return html_content

        except PlaywrightTimeout:
            logger.error(f"Timeout while loading profile: {url}")
            return None

        except Exception as e:
            logger.error(f"Error fetching HTML: {str(e)}")
            return None

    def _clean_html(self, html: str) -> str:
        
        soup = BeautifulSoup(html, 'html.parser')

        
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        
        text_content = soup.get_text(separator='\n', strip=True)

       
        text_content = re.sub(r'\n\s*\n+', '\n\n', text_content)

        logger.info(f"Extracted text content ({len(text_content)} characters)")

       
        max_chars = 400000  
        if len(text_content) > max_chars:
            logger.warning(f"Text content truncated from {len(text_content)} to {max_chars} characters")
            text_content = text_content[:max_chars]

        
        try:
            with open('extracted_text.txt', 'w', encoding='utf-8') as f:
                f.write(text_content)
            logger.info("Saved extracted text to: extracted_text.txt")
        except Exception as e:
            logger.warning(f"Could not save extracted text: {e}")

        return text_content

    def _extract_with_llm(self, html_content: str, url: str, max_retries: int = 3) -> Dict[str, Optional[str]]:
        
        for attempt in range(max_retries):
            try:
                prompt = f"""Extract the following information from this LinkedIn profile HTML:

1. name: The person's full name
2. title: Their current job title/position
3. company: Their current company/organization
4. about: The content of their "About" section (if available)

HTML Content:
{html_content}

CRITICAL INSTRUCTIONS:
- Return ONLY a valid JSON object, nothing else
- No markdown formatting, no code blocks, no explanatory text
- Use null for fields you cannot find
- Do not invent or guess information

Required JSON format:
{{"name": "value or null", "title": "value or null", "company": "value or null", "about": "value or null"}}"""

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a data extraction assistant. You ONLY respond with valid JSON. Never add explanatory text, markdown formatting, or code blocks. Return pure JSON only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0,
                    max_tokens=1000,
                    response_format={"type": "json_object"} 
                )

               
                response_text = response.choices[0].message.content.strip()

               
                response_text = re.sub(r'^```json\s*', '', response_text)
                response_text = re.sub(r'^```\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)
                response_text = response_text.strip()

                
                parsed_data = json.loads(response_text)

                
                profile = LinkedInProfile(**parsed_data)

               
                profile_data = profile.model_dump()
                profile_data['url'] = url

                logger.info(f" Successfully extracted profile data for: {profile_data.get('name', 'Unknown')}")
                return profile_data

            except json.JSONDecodeError as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: JSON parse error - {str(e)}")
                logger.debug(f"Response was: {response_text[:500]}")

                if attempt == max_retries - 1:
                    return {
                        'name': None,
                        'title': None,
                        'company': None,
                        'about': None,
                        'url': url,
                        'error': f'Failed to parse valid JSON after {max_retries} attempts'
                    }

            except ValidationError as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: Pydantic validation error - {str(e)}")

                if attempt == max_retries - 1:
                    return {
                        'name': None,
                        'title': None,
                        'company': None,
                        'about': None,
                        'url': url,
                        'error': f'Failed to validate response schema after {max_retries} attempts'
                    }

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries}: Unexpected error - {str(e)}")

                if attempt == max_retries - 1:
                    return {
                        'name': None,
                        'title': None,
                        'company': None,
                        'about': None,
                        'url': url,
                        'error': f'LLM extraction error: {str(e)}'
                    }

       
        return {
            'name': None,
            'title': None,
            'company': None,
            'about': None,
            'url': url,
            'error': 'Unknown error during extraction'
        }


def scrape_linkedin_profile(url: str) -> Dict[str, Optional[str]]:
    
    scraper = LinkedInScraper(headless=Config.HEADLESS_MODE)
    return scraper.scrape_profile(url)
