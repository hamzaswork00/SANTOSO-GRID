"""
SANTOSO-GRID - Email Sender Engine
Mass email sending with threading and anti-detection
Version: 1.0
"""

import smtplib
import email.utils as eut
import time
import random
import threading
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional, Dict

from proxy_manager import ProxyManager
from telegram_bot import TelegramBot
from anti_detection import AntiDetection
from database import Database

class EmailSender:
    """Mass email sender engine"""
    
    def __init__(
        self,
        from_name: str,
        from_email: str,
        subject: str,
        content: str,
        content_type: str,
        maillist: List[str],
        proxy_type: Optional[str],
        proxy_manager: ProxyManager,
        telegram_bot: Optional[TelegramBot],
        anti_detection: AntiDetection,
        settings: Dict
    ):
        self.from_name = from_name
        self.from_email = from_email
        self.subject = subject
        self.content = content
        self.content_type = content_type
        self.maillist = maillist
        self.proxy_type = proxy_type
        self.proxy_manager = proxy_manager
        self.telegram_bot = telegram_bot
        self.anti_detection = anti_detection
        self.settings = settings
        
        # Status tracking
        self.running = False
        self.paused = False
        self.sent = 0
        self.failed = 0
        self.current_email = None
        self.start_time = None
        self.proxy_rotation_count = 500
        
        # Email queue
        self.queue = []
        self.queue_lock = threading.Lock()
        
    async def start_sending(self, campaign_id: int):
        """Start the sending process"""
        self.running = True
        self.start_time = datetime.now()
        
        # Load proxies if using
        if self.proxy_type:
            await self.proxy_manager.load_from_file()
        
        # Create email queue
        with self.queue_lock:
            self.queue = list(self.maillist)
        
        # Calculate delay for 5000/hour = ~0.72 seconds between emails
        base_delay = 3600 / 5000
        
        while self.running and self.queue:
            if self.paused:
                await asyncio.sleep(1)
                continue
            
            # Get next email
            with self.queue_lock:
                if not self.queue:
                    break
                recipient = self.queue.pop(0)
            
            self.current_email = recipient
            
            try:
                # Send email
                success = await self.send_email(recipient)
                
                if success:
                    self.sent += 1
                else:
                    self.failed += 1
                self.current_email = None
                
                # Report every 5000 emails
                if self.sent > 0 and self.sent % 5000 == 0:
                    await self.send_telegram_report(campaign_id)
                
                # Rotate proxy every X emails
                if self.proxy_type and self.sent % self.proxy_rotation_count == 0:
                    self.proxy_manager.rotate_proxy()
                
                # Random delay for anti-detection
                delay = random.uniform(0.5, 2.0)
                await asyncio.sleep(delay)
                
            except Exception as e:
                self.failed += 1
                print(f"Error sending to {recipient}: {e}")
        
        # Campaign complete
        await self.send_telegram_report(campaign_id, final=True)
        self.running = False
    
    async def send_email(self, recipient: str) -> bool:
        """Send a single email"""
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient
            msg['Subject'] = self.subject
            
            # Apply anti-detection to headers
            msg = self.anti_detection.randomize_headers(msg)
            
            # Add content
            if self.content_type == "html":
                # Apply content obfuscation
                content = self.anti_detection.obfuscize_content(self.content)
                msg.attach(MIMEText(content, 'html'))
            else:
                msg.attach(MIMEText(self.content, 'plain'))
            
            # Get proxy if using
            proxy = None
            if self.proxy_type:
                proxy = self.proxy_manager.get_current_proxy()
            
            # Connect to SMTP
            if proxy:
                # Use proxy
                server = smtplib.SMTP(proxy['host'], proxy['port'], timeout=30)
            else:
                # Direct SMTP (localhost)
                server = smtplib.SMTP('localhost', 25, timeout=30)
            
            # Send email
            server.sendmail(self.from_email, recipient, msg.as_string())
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    async def send_telegram_report(self, campaign_id: int, final: bool = False):
        """Send progress report to Telegram"""
        if not self.telegram_bot:
            return
        
        remaining = len(self.queue)
        elapsed = (datetime.now() - self.start_time).seconds if self.start_time else 0
        speed = int(self.sent / (elapsed / 3600)) if elapsed > 0 else 0
        
        text = f"""📧 SANTOSO-GRID Report - Campaign #{campaign_id}
✅ Sent: {self.sent:,}
⏳ Remaining: {remaining:,}
❌ Failed: {self.failed:,}
📊 Speed: {speed}/hour
🔗 Current: {self.current_email or 'N/A'}"""
        
        if final:
            text += "\n\n🎉 Campaign Complete!"
        
        await self.telegram_bot.send_message(text)
    
    def stop(self):
        """Stop the sending process"""
        self.running = False
    
    def pause(self):
        """Pause the sending process"""
        self.paused = True
    
    def resume(self):
        """Resume the sending process"""
        self.paused = False
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            "running": self.running,
            "paused": self.paused,
            "sent": self.sent,
            "failed": self.failed,
            "remaining": len(self.queue),
            "current": self.current_email,
            "start_time": self.start_time.isoformat() if self.start_time else None
        }