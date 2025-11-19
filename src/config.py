

import os
from dotenv import load_dotenv
from typing import Literal


load_dotenv()


class Config:
    """Application configuration class"""

   
    PROVIDER = os.getenv('PROVIDER', 'auto').lower()

    
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_DEPLOYMENT_NAME = os.getenv('AZURE_DEPLOYMENT_NAME')
    AZURE_API_VERSION = os.getenv('AZURE_API_VERSION', '2025-01-01-preview')

    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

    
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))

    
    LOGIN_METHOD = os.getenv('LOGIN_METHOD', 'credentials').lower() 
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
    CHROME_USER_DATA_DIR = os.getenv('CHROME_USER_DATA_DIR')

    
    HEADLESS_MODE = True 
    PAGE_LOAD_TIMEOUT = 60  
    IMPLICIT_WAIT = 10

    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def get_provider(cls) -> Literal['azure', 'openai']:
       
        if cls.PROVIDER in ['azure', 'openai']:
            provider = cls.PROVIDER
           
            if provider == 'azure' and (not cls.AZURE_OPENAI_API_KEY or not cls.AZURE_OPENAI_ENDPOINT):
                raise ValueError(f"PROVIDER is set to 'azure' but Azure credentials are missing")
            if provider == 'openai' and not cls.OPENAI_API_KEY:
                raise ValueError(f"PROVIDER is set to 'openai' but OPENAI_API_KEY is missing")
            return provider

       
        if cls.AZURE_OPENAI_API_KEY and cls.AZURE_OPENAI_ENDPOINT:
            return 'azure'
        elif cls.OPENAI_API_KEY:
            return 'openai'
        else:
            raise ValueError("No OpenAI credentials found. Please set either Azure or OpenAI credentials in .env")

    @classmethod
    def validate(cls):
        
        provider = cls.get_provider()

        if provider == 'azure':
            if not cls.AZURE_OPENAI_API_KEY:
                raise ValueError("AZURE_OPENAI_API_KEY not found in environment variables")
            if not cls.AZURE_OPENAI_ENDPOINT:
                raise ValueError("AZURE_OPENAI_ENDPOINT not found in environment variables")
            if not cls.AZURE_DEPLOYMENT_NAME:
                raise ValueError("AZURE_DEPLOYMENT_NAME not found in environment variables")
            print(f"[OK] Using Azure OpenAI: {cls.AZURE_OPENAI_ENDPOINT}")
        else:
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            print(f"[OK] Using OpenAI with model: {cls.OPENAI_MODEL}")

        return True


def get_openai_client():
    
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
   
    provider = Config.get_provider()

    if provider == 'azure':
        return Config.AZURE_DEPLOYMENT_NAME
    else:
        return Config.OPENAI_MODEL



try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please check your .env file and ensure either Azure or OpenAI credentials are set.")
