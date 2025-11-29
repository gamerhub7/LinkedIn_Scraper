"""
LinkedIn Email Generator - Main Application
Orchestrates profile scraping and email generation
"""

import sys
import json
import logging
from typing import Dict, Optional

from .config import Config
from .linkedin_scraper import scrape_linkedin_profile
from .email_generator import generate_personalized_email
from .utils import (
    validate_linkedin_url,
    create_error_response,
    log_profile_info,
    format_json_output
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_linkedin_profile(url: str) -> Dict:
    """
    Process a LinkedIn profile URL and generate a personalized email

    Args:
        url: LinkedIn profile URL

    Returns:
        Dictionary containing profile info and generated email in the format:
        {
            "name": "John Doe",
            "title": "Software Engineer at Google",
            "company": "Google",
            "about": "Passionate about AI...",
            "email": {
                "subject": "...",
                "body": "..."
            }
        }
    """
    logger.info(f"Processing LinkedIn profile: {url}")

    # Validate URL
    if not validate_linkedin_url(url):
        logger.error(f"Invalid LinkedIn URL: {url}")
        return create_error_response("Invalid LinkedIn URL format", url)

    # Step 1: Scrape LinkedIn profile
    logger.info("Step 1: Scraping LinkedIn profile...")
    profile_data = scrape_linkedin_profile(url)

    # Check for scraping errors
    if 'error' in profile_data:
        logger.error(f"Scraping error: {profile_data['error']}")
        return create_error_response(profile_data['error'], url)

    # Log profile information
    log_profile_info(profile_data)

    # Check if we have enough data
    if not profile_data.get('name'):
        logger.warning("Profile name not found - profile may not be public or accessible")
        return create_error_response(
            "Unable to extract profile information. Profile may require login or is not public.",
            url
        )

    # Step 2: Generate personalized email
    logger.info("Step 2: Generating personalized email...")
    email_data = generate_personalized_email(profile_data)

    # Check for email generation errors
    if 'error' in email_data:
        logger.error(f"Email generation error: {email_data['error']}")
        # Still return profile data with error
        return {
            'name': profile_data.get('name'),
            'title': profile_data.get('title'),
            'company': profile_data.get('company'),
            'about': profile_data.get('about'),
            'email': None,
            'error': email_data['error'],
            'status': 'partial_success'
        }

    # Step 3: Combine results
    result = {
        'name': profile_data.get('name'),
        'title': profile_data.get('title'),
        'company': profile_data.get('company'),
        'about': profile_data.get('about'),
        'email': {
            'subject': email_data.get('subject'),
            'body': email_data.get('body')
        }
    }

    # Add warning if about section is missing
    if not profile_data.get('about'):
        result['warning'] = 'About section not found, email generated from available data'

    logger.info("Successfully completed processing!")
    return result


def main():
    """
    Main entry point for the application
    Accepts LinkedIn URL as command-line argument
    """
    # Check if URL is provided
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <linkedin_profile_url>")
        print("Example: python -m src.main https://www.linkedin.com/in/johndoe")
        sys.exit(1)

    url = sys.argv[1]

    try:
        # Process the profile
        result = process_linkedin_profile(url)

        # Output JSON result
        print("\n" + "=" * 70)
        print("RESULT:")
        print("=" * 70)
        print(format_json_output(result))
        print("=" * 70)

        # Exit with appropriate code
        if 'error' in result:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        error_result = create_error_response(f"Unexpected error: {str(e)}", url)
        print(format_json_output(error_result))
        sys.exit(1)


if __name__ == '__main__':
    main()
