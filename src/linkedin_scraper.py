"""
LinkedIn Profile Scraper - LLM-based extraction
Fetches HTML and uses OpenAI to extract profile information
This is more robust than CSS selector-based scraping
"""

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
    """Pydantic model for LinkedIn profile data validation"""
    name: Optional[str] = Field(None, description="Person's full name")
    title: Optional[str] = Field(None, description="Current job title/position")
    company: Optional[str] = Field(None, description="Current company/organization")
    about: Optional[str] = Field(None, description="About section content")


import google.generativeai as genai

class LinkedInScraper:
    """
    LinkedIn profile scraper that uses LLM for extraction
    Instead of fragile CSS selectors, we clean the HTML and let the LLM extract information
    """

    def __init__(self, headless: bool = True, email: Optional[str] = None, password: Optional[str] = None, llm_provider: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the LinkedIn scraper

        Args:
            headless: Run browser in headless mode (default: True)
            email: LinkedIn email (optional, overrides config)
            password: LinkedIn password (optional, overrides config)
            llm_provider: LLM provider (optional, overrides config)
            api_key: API key for the provider (optional, overrides config)
        """
        self.headless = headless
        self.email = email
        self.password = password
        
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
            self.client = None # Not used for Gemini
        else:
            # For OpenAI/Azure, we might need to handle dynamic keys differently
            # But for now, we'll assume standard Config or environment variables if not provided
            # If api_key is provided for OpenAI, we'd need to pass it to the client
            if self.api_key and self.provider == 'openai':
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            else:
                self.client = get_openai_client()
            self.model = get_model_name()

    def scrape_profile(self, url: str) -> Dict[str, Optional[str]]:
        """
        Scrape LinkedIn profile information using LLM extraction

        Args:
            url: LinkedIn profile URL

        Returns:
            Dictionary containing profile information
        """
        try:
            # Step 1: Fetch HTML
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

            # Step 2: Clean HTML
            logger.info("Cleaning HTML content...")
            cleaned_html = self._clean_html(html_content)

            # Step 3: Extract information using LLM
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
        """
        Login to LinkedIn using credentials from config

        Args:
            page: Playwright page object

        Returns:
            True if login successful, False otherwise
        """
        try:
            # Use instance credentials if provided, otherwise fallback to Config
            email = self.email or Config.LINKEDIN_EMAIL
            password = self.password or Config.LINKEDIN_PASSWORD

            if not email or not password:
                logger.info("No LinkedIn credentials provided, skipping login")
                return False

            logger.info("Logging in to LinkedIn...")

            # Navigate to login page
            page.goto('https://www.linkedin.com/checkpoint/rm/sign-in-another-account', wait_until='networkidle')
            page.wait_for_timeout(2000)

            # Fill in username
            logger.info("Entering credentials...")
            page.fill('input[id="username"]', email)
            page.wait_for_timeout(500)

            # Fill in password
            page.fill('input[id="password"]', password)
            page.wait_for_timeout(500)

            # Click sign in button
            page.click('button[aria-label="Sign in"]')
            logger.info("Clicked sign in button, waiting for login...")

            # Wait for navigation after login
            page.wait_for_timeout(5000)

            # Check if login was successful (look for common logged-in elements)
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
        """
        Click all "see more" buttons to expand truncated sections

        Args:
            page: Playwright page object
        """
        try:
            logger.info("Looking for 'see more' buttons to expand sections...")

            # Find all buttons with role="button" that contain "see more" text
            # This targets the About section and other expandable sections
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
                    # Find all matching buttons
                    buttons = page.locator(selector).all()

                    for button in buttons:
                        try:
                            # Check if button is visible
                            if button.is_visible():
                                logger.info(f"Clicking 'see more' button...")
                                button.click()
                                clicked_count += 1
                                # Wait for content to expand
                                page.wait_for_timeout(1000)
                        except Exception as e:
                            # Button might not be clickable or already clicked
                            logger.debug(f"Could not click button: {str(e)}")
                            continue

                except Exception as e:
                    logger.debug(f"No buttons found for selector '{selector}': {str(e)}")
                    continue

            if clicked_count > 0:
                logger.info(f"[OK] Clicked {clicked_count} 'see more' button(s)")
                # Wait for all expansions to complete
                page.wait_for_timeout(2000)
            else:
                logger.info("No 'see more' buttons found (sections may already be expanded)")

        except Exception as e:
            logger.warning(f"Error expanding sections: {str(e)}")
            # Continue anyway - not a critical failure

    def _fetch_profile_html(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content of a LinkedIn profile using Playwright

        Args:
            url: LinkedIn profile URL

        Returns:
            HTML content as string, or None if failed
        """
        try:
            with sync_playwright() as p:
                # Determine login method based on config
                login_method = Config.LOGIN_METHOD

                logger.info(f"Login method: {login_method}")

                # Method 1: Use Chrome profile (stays logged in)
                if login_method == 'chrome_profile' and Config.CHROME_USER_DATA_DIR:
                    logger.info(f"Using Chrome profile: {Config.CHROME_USER_DATA_DIR}")

                    # Clean the path (remove quotes if present)
                    chrome_path = Config.CHROME_USER_DATA_DIR.strip('"').strip("'")

                    # Use launch_persistent_context for user data
                    context = p.chromium.launch_persistent_context(
                        chrome_path,
                        headless=self.headless,
                        channel='chrome',
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        viewport={'width': 1920, 'height': 1080}
                    )

                    # Create new page
                    page = context.new_page()

                # Method 2: Use LinkedIn credentials
                elif login_method == 'credentials':
                    logger.info("Using LinkedIn credentials for login")

                    # Regular browser launch without profile
                    browser = p.chromium.launch(headless=self.headless)

                    # Create context with custom user agent
                    context = browser.new_context(
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        viewport={'width': 1920, 'height': 1080}
                    )

                    # Create new page
                    page = context.new_page()

                    # Login with credentials
                    self._login_to_linkedin(page)

                # Method 3: No login (may not work for most profiles)
                else:
                    logger.warning("No login method configured - scraping may fail for private profiles")

                    # Regular browser launch without profile
                    browser = p.chromium.launch(headless=self.headless)

                    # Create context with custom user agent
                    context = browser.new_context(
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        viewport={'width': 1920, 'height': 1080}
                    )

                    # Create new page
                    page = context.new_page()

                # Navigate to the profile
                logger.info(f"Navigating to profile: {url}")
                page.goto(url, wait_until='domcontentloaded', timeout=Config.PAGE_LOAD_TIMEOUT * 1000)

                # Wait for content to load (increased wait time)
                page.wait_for_timeout(5000)

                # Click "see more" buttons to expand sections (especially About)
                self._expand_see_more_sections(page)

                # Get page content
                html_content = page.content()

                # Close context/browser
                context.close()

                return html_content

        except PlaywrightTimeout:
            logger.error(f"Timeout while loading profile: {url}")
            return None

        except Exception as e:
            logger.error(f"Error fetching HTML: {str(e)}")
            return None

    def _clean_html(self, html: str) -> str:
        """
        Extract text content from HTML for LLM extraction
        Remove scripts/styles but keep all text

        Args:
            html: Raw HTML content

        Returns:
            Cleaned text content
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script, style, and noscript tags
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        # Extract all text content (this is much smaller than full HTML)
        text_content = soup.get_text(separator='\n', strip=True)

        # Remove excessive newlines
        text_content = re.sub(r'\n\s*\n+', '\n\n', text_content)

        logger.info(f"Extracted text content ({len(text_content)} characters)")

        # Truncate if still too long (Azure GPT-4o has ~128K token limit ≈ 512K chars)
        max_chars = 400000  # Increased to capture full profile including About section
        if len(text_content) > max_chars:
            logger.warning(f"Text content truncated from {len(text_content)} to {max_chars} characters")
            text_content = text_content[:max_chars]

        # Save extracted text to file for debugging
        try:
            with open('extracted_text.txt', 'w', encoding='utf-8') as f:
                f.write(text_content)
            logger.info("Saved extracted text to: extracted_text.txt")
        except Exception as e:
            logger.warning(f"Could not save extracted text: {e}")

        return text_content

    def _extract_with_llm(self, html_content: str, url: str, max_retries: int = 3) -> Dict[str, Optional[str]]:
        """
        Use LLM (OpenAI or Gemini) to extract profile information from cleaned HTML
        Uses Pydantic for validation and retries on failure

        Args:
            html_content: Cleaned HTML content
            url: Profile URL
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary with extracted profile data
        """
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

                response_text = ""

                if self.provider == 'gemini':
                    # Gemini Call
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.GenerationConfig(
                            temperature=0.0,
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
                                "content": "You are a data extraction assistant. You ONLY respond with valid JSON. Never add explanatory text, markdown formatting, or code blocks. Return pure JSON only."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0,
                        max_tokens=1000,
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
                profile = LinkedInProfile(**parsed_data)

                # Convert to dict and add URL
                profile_data = profile.model_dump()
                profile_data['url'] = url

                logger.info(f"✓ Successfully extracted profile data for: {profile_data.get('name', 'Unknown')}")
                return profile_data

            except Exception as e:
                # ... (error handling remains similar) ...
                logger.error(f"Attempt {attempt + 1}/{max_retries}: Error - {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        'name': None,
                        'title': None,
                        'company': None,
                        'about': None,
                        'url': url,
                        'error': f'Extraction error: {str(e)}'
                    }

        # This should never be reached, but just in case
        return {
            'name': None,
            'title': None,
            'company': None,
            'about': None,
            'url': url,
            'error': 'Unknown error during extraction'
        }





def scrape_linkedin_profile(url: str) -> Dict[str, Optional[str]]:
    """
    Convenience function to scrape a LinkedIn profile

    Args:
        url: LinkedIn profile URL

    Returns:
        Dictionary containing profile information
    """
    scraper = LinkedInScraper(headless=Config.HEADLESS_MODE)
    return scraper.scrape_profile(url)

