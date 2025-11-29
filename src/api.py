from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os

from src.linkedin_scraper import LinkedInScraper
from src.email_generator import generate_personalized_email
from src.config import Config

app = FastAPI(title="LinkedIn Email Generator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    url: str
    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None
    llm_provider: Optional[str] = None
    api_key: Optional[str] = None

import traceback

@app.post("/api/generate")
def generate_email(request: GenerateRequest):
    try:
        # Initialize scraper with provided credentials and LLM config
        scraper = LinkedInScraper(
            headless=Config.HEADLESS_MODE,
            email=request.linkedin_email,
            password=request.linkedin_password,
            llm_provider=request.llm_provider,
            api_key=request.api_key
        )
        
        # Scrape profile
        profile_data = scraper.scrape_profile(request.url)
        
        if profile_data.get('error'):
            raise HTTPException(status_code=400, detail=profile_data['error'])
            
        # Generate email
        email_data = generate_personalized_email(
            profile_data,
            llm_provider=request.llm_provider,
            api_key=request.api_key
        )
        
        return {
            "profile": profile_data,
            "email": email_data
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend static files (after building)
# We'll assume the frontend is built to 'frontend/dist'
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"Warning: Frontend build not found at {frontend_path}")
