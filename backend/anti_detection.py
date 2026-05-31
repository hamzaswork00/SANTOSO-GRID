"""
SANTOSO-GRID - Anti-Detection System
Randomize headers and content to avoid spam detection
Version: 1.0
"""

import random
import string
import uuid
import email
from email.mime.message import MIMEMessage
from typing import Dict, List
from datetime import datetime
import time

class AntiDetection:
    """Anti-detection features for email sending"""
    
    def __init__(self):
        # Mailer variations
        self.mailers = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5) AppleWebKit/605.1.15",
        ]
        
        # Message-ID domains
        self.message_id_domains = [
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
            "mail.com", "protonmail.com", "icloud.com", "aol.com"
        ]
        
        # X-Priority values
        self.priorities = ["1", "2", "3"]
    
    def randomize_headers(self, msg) -> email.message.Message:
        """Add randomized headers to email"""
        
        # Generate unique Message-ID
        message_id = f"<{uuid.uuid4().hex}@{random.choice(self.message_id_domains)}>"
        msg['Message-ID'] = message_id
        
        # Random X-Mailer
        msg['X-Mailer'] = random.choice(self.mailers)
        
        # Random X-Priority
        msg['X-Priority'] = random.choice(self.priorities)
        
        # Add some common headers
        msg['X-MSMail-Priority'] = random.choice(['Normal', 'High'])
        msg['X-Mailer-Actor'] = random.choice(['User', 'System', 'Auto'])
        
        # Add some obfuscated headers
        msg['X-Originating-IP'] = f"[{self.generate_random_ip()}]"
        
        # DKIM-Signature if available (will be added by mail server)
        # msg['DKIM-Signature'] = "..."
        
        return msg
    
    def generate_random_ip(self) -> str:
        """Generate random IP address"""
        # Use private IP ranges
        return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    
    def obfuscize_content(self, content: str) -> str:
        """Add invisible characters to content"""
        
        # Add zero-width characters randomly
        zero_width_space = "\u200B"
        zero_width_non_joiner = "\u200C"
        zero_width_joiner = "\u200D"
        
        # Sometimes add invisible characters
        if random.random() < 0.3:
            # Insert in random places
            chars = list(content)
            for i in range(random.randint(1, 3)):
                pos = random.randint(0, len(chars))
                insert_char = random.choice([zero_width_space, zero_width_non_joiner])
                chars.insert(pos, insert_char)
            content = "".join(chars)
        
        # Add random HTML comments if HTML content
        if "<html" in content.lower() or "<div" in content.lower():
            # Insert random comments
            comment = f"<!--{random.randint(1000,9999)}-->"
            if random.random() < 0.3:
                # Random position
                parts = content.split(">", 1)
                if len(parts) > 1:
                    content = parts[0] + ">" + comment + parts[1]
        
        return content
    
    def generate_bounce_address(self) -> str:
        """Generate bounce address"""
        bounce_id = uuid.uuid4().hex[:16]
        return f"bounce-{bounce_id}@localhost"
    
    def generate_list_unsubscribe(self) -> str:
        """Generate list-unsubscribe header"""
        return f"<mailto:bounce@localhost?subject=unsubscribe>"
    
    def add_stealth_headers(self, msg) -> email.message.Message:
        """Add stealth headers to avoid detection"""
        
        # Add Received header (simulating routing)
        received = f"from localhost (localhost [127.0.0.1]) by localhost with SMTP"
        msg['Received'] = received
        
        # Add thread info
        msg['Thread-Index'] = uuid.uuid().hex[:32]
        msg['Thread-Topic'] = random.choice(['General', 'Updates', 'Newsletter'])
        
        return msg
    
    def prepare_for_warming(self, msg) -> email.message.Message:
        """Prepare email for warming (progressive sending)"""
        
        # Lower priority for warming
        msg['X-Priority'] = "3"
        msg['X-MSMail-Priority'] = "Normal"
        
        # AddPrecedence
        msg['Precedence'] = "bulk"
        
        # Auto-submit
        msg['Auto-Submitted'] = "auto-generated"
        
        return msg
    
    def detect_bounce(self, message: str) -> Dict:
        """Detect bounce from message"""
        bounce_indicators = [
            "delivery failed",
            "undelivered",
            "returned",
            "mailbox full",
            "user unknown",
            "address not found",
            "550",
            "recipient rejected"
        ]
        
        message_lower = message.lower()
        
        for indicator in bounce_indicators:
            if indicator in message_lower:
                return {
                    "is_bounce": True,
                    "type": indicator,
                    "email": self.extract_email_from_message(message)
                }
        
        return {"is_bounce": False}
    
    def extract_email_from_message(self, message: str) -> str:
        """Extract email address from message"""
        import re
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, message)
        
        return matches[0] if matches else None
    
    def clean_list(self, emails: List[str]) -> List[str]:
        """Clean email list from invalid addresses"""
        import re
        
        cleaned = []
        
        for email_addr in emails:
            email_addr = email_addr.strip()
            
            # Basic validation
            email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
            
            if re.match(email_pattern, email_addr):
                # Check for disposable domains
                disposable_domains = [
                    "tempmail.com", "throwaway.com", "10minutemail.com",
                    "guerrillamail.com", "mailinator.com"
                ]
                
                domain = email_addr.split("@")[-1].lower()
                
                if domain not in disposable_domains:
                    cleaned.append(email_addr)
        
        return cleaned