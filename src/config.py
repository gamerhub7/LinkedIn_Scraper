"""
Configuration module for LinkedIn Email Generator
Handles environment variables and application settings
Supports both Azure OpenAI and regular OpenAI
"""

import os
from dotenv import load_dotenv
from typing import Literal

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""

    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai") # openai, azure, gemini
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Azure OpenAI
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
    AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # Rate Limiting
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))

    # LinkedIn Login Configuration
    LOGIN_METHOD = os.getenv('LOGIN_METHOD', 'credentials').lower()  # 'chrome_profile', 'credentials', or 'none'
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
    CHROME_USER_DATA_DIR = os.getenv('CHROME_USER_DATA_DIR')

    # Playwright Configuration
    HEADLESS_MODE = True # Set to True to run in headless mode
    PAGE_LOAD_TIMEOUT = 60  # Increased to 60 seconds
    IMPLICIT_WAIT = 10

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def get_provider(cls) -> Literal['azure', 'openai', 'gemini']:
        """
        Determine which LLM provider to use based on LLM_PROVIDER setting or auto-detection

        Returns:
            'azure', 'openai', or 'gemini'
        """
        # If explicitly set, use that
        if cls.LLM_PROVIDER in ['azure', 'openai', 'gemini']:
            provider = cls.LLM_PROVIDER
            # Validate that the required credentials exist for this provider
            if provider == 'azure' and (not cls.AZURE_OPENAI_API_KEY or not cls.AZURE_OPENAI_ENDPOINT):
                raise ValueError(f"LLM_PROVIDER is set to 'azure' but Azure credentials are missing")
            if provider == 'openai' and not cls.OPENAI_API_KEY:
                raise ValueError(f"LLM_PROVIDER is set to 'openai' but OPENAI_API_KEY is missing")
            if provider == 'gemini' and not cls.GEMINI_API_KEY:
                raise ValueError(f"LLM_PROVIDER is set to 'gemini' but GEMINI_API_KEY is missing")
            return provider

        # Auto-detect based on available credentials
        if cls.GEMINI_API_KEY:
            return 'gemini'
        elif cls.AZURE_OPENAI_API_KEY and cls.AZURE_OPENAI_ENDPOINT:
            return 'azure'
        elif cls.OPENAI_API_KEY:
            return 'openai'
        else:
            raise ValueError("No LLM credentials found. Please set Azure, OpenAI, or Gemini credentials in .env")

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        provider = cls.get_provider()

        if provider == 'azure':
            if not cls.AZURE_OPENAI_API_KEY:
                raise ValueError("AZURE_OPENAI_API_KEY not found in environment variables")
            print(f"[OK] Using Azure OpenAI: {cls.AZURE_OPENAI_ENDPOINT}")
        elif provider == 'gemini':
            if not cls.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            print(f"[OK] Using Gemini: {cls.GEMINI_MODEL}")
        else:
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            print(f"[OK] Using OpenAI with model: {cls.OPENAI_MODEL}")

        return True


def get_openai_client():
    """
    Factory function to get the appropriate OpenAI client based on configuration

    Returns:
        Either AzureOpenAI or OpenAI client instance
    """
    from openai import OpenAI, AzureOpenAI

    provider = Config.get_provider()

    if provider == 'azure':
        return AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
    else:
        return OpenAI(api_key=Config.OPENAI_API_KEY)


def get_model_name():
    """
    Get the appropriate model/deployment name based on provider

    Returns:
        Model name for OpenAI or deployment name for Azure OpenAI
    """
    provider = Config.get_provider()

    if provider == 'azure':
        return Config.AZURE_DEPLOYMENT_NAME
    else:
        return Config.OPENAI_MODEL


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please check your .env file and ensure either Azure or OpenAI credentials are set.")
