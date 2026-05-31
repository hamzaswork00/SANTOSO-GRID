"""
SANTOSO-GRID - Telegram Bot
Send notifications to Telegram
Version: 1.0
"""

import asyncio
from typing import Optional
import requests

class TelegramBot:
    """Telegram bot notifications"""
    
    def __init__(self, token: str, user_id: str):
        self.token = token
        self.user_id = user_id
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.enabled = bool(token and user_id and token != "your_bot_token_here")
    
    async def send_message(self, text: str):
        """Send message to Telegram"""
        if not self.enabled:
            return
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": self.user_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(url, data=data, timeout=10)
            )
            
        except Exception as e:
            print(f"Telegram error: {e}")
    
    async def send_photo(self, photo_url: str, caption: str = None):
        """Send photo to Telegram"""
        if not self.enabled:
            return
        
        try:
            url = f"{self.api_url}/sendPhoto"
            data = {
                "chat_id": self.user_id,
                "photo": photo_url
            }
            
            if caption:
                data["caption"] = caption
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(url, data=data, timeout=10)
            )
            
        except Exception as e:
            print(f"Telegram error: {e}")
    
    async def send_document(self, file_path: str, caption: str = None):
        """Send document to Telegram"""
        if not self.enabled:
            return
        
        try:
            url = f"{self.api_url}/sendDocument"
            data = {
                "chat_id": self.user_id,
            }
            
            files = {"document": open(file_path, "rb")}
            
            if caption:
                data["caption"] = caption
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(url, data=data, files=files, timeout=30)
            )
            
        except Exception as e:
            print(f"Telegram error: {e}")
    
    async def test_connection(self) -> bool:
        """Test bot connection"""
        if not self.enabled:
            return False
        
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False