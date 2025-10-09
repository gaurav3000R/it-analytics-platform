# Adding the missing ./backend/app/utils/gemini_client.py (required for Gemini integration)

#===== ./backend/app/utils/gemini_client.py =====

import os
import time
import logging
from typing import Any, Optional

import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

def get_gemini_client():
    """Initialize and return Gemini client"""
    if not settings.GOOGLE_API_KEY:
        logger.warning("GOOGLE_API_KEY not set in environment. Gemini features will be disabled.")
        return None
    
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    return GeminiClient()

class GeminiClient:
    def __init__(self):
        self.primary_model = genai.GenerativeModel(settings.GEMINI_PRIMARY_MODEL)
        self.fallback_model = genai.GenerativeModel(settings.GEMINI_FALLBACK_MODEL)
        
    async def generate_content_with_retry(
        self,
        prompt: str,
        text_only: bool = True,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> str:
        """Generate content with retry logic"""
        current_model = self.primary_model
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = current_model.generate_content(prompt)
                
                if text_only:
                    return response.text
                return response
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Gemini generation failed (attempt {retry_count}/{max_retries}): {e}")
                
                if retry_count == max_retries:
                    raise RuntimeError(f"Failed to generate content after {max_retries} retries: {e}")
                
                # Switch to fallback model if primary fails
                if current_model == self.primary_model:
                    logger.info("Switching to fallback model")
                    current_model = self.fallback_model
                
                # Exponential backoff
                sleep_time = backoff_factor ** retry_count
                time.sleep(sleep_time)
        
        raise RuntimeError("Unexpected error in content generation")