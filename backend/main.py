#!/usr/bin/env python3
"""
SANTOSO-GRID - Main Backend Application
FastAPI Server with all endpoints
Version: 1.0
"""

import os
import sys
import asyncio
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

# Import custom modules
from sender import EmailSender
from proxy_manager import ProxyManager
from telegram_bot import TelegramBot
from anti_detection import AntiDetection
from database import Database

# Initialize FastAPI app
app = FastAPI(title="SANTOSO-GRID", version="1.0")

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Initialize modules
db = Database(DATA_DIR / "santosogrid.db")
proxy_manager = ProxyManager()
telegram_bot = None
anti_detection = AntiDetection()
email_sender = None

# Templates
templates = Jinja2Templates(BASE_DIR / "frontend")

# === API MODELS ===

class CampaignStart(BaseModel):
    from_name: str
    from_email: str
    subject: str
    content: str
    content_type: str  # "text" or "html"
    maillist: List[str]
    proxy_type: Optional[str] = None

class ProxyCheck(BaseModel):
    proxies: List[str]

class TemplateSave(BaseModel):
    name: str
    content: str
    content_type: str

class MaillistFilter(BaseModel):
    emails: List[str]
    domains: List[str]

# === ROUTES ===

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": {}})

@app.get("/send", response_class=HTMLResponse)
async def send_page():
    """Email sender page"""
    return templates.TemplateResponse("send.html", {"request": {}})

@app.get("/proxy", response_class=HTMLResponse)
async def proxy_page():
    """Proxy checker page"""
    return templates.TemplateResponse("proxy.html", {"request": {}})

@app.get("/filter", response_class=HTMLResponse)
async def filter_page():
    """Maillist filter page"""
    return templates.TemplateResponse("filter.html", {"request": {}})

@app.get("/templates", response_class=HTMLResponse)
async def templates_page():
    """Templates manager page"""
    return templates.TemplateResponse("templates.html", {"request": {}})

# === API ENDPOINTS ===

@app.post("/api/start-campaign")
async def start_campaign(campaign: CampaignStart):
    """Start email sending campaign"""
    global email_sender
    
    try:
        # Get settings
        settings = db.get_settings()
        
        # Initialize sender
        email_sender = EmailSender(
            from_name=campaign.from_name,
            from_email=campaign.from_email,
            subject=campaign.subject,
            content=campaign.content,
            content_type=campaign.content_type,
            maillist=campaign.maillist,
            proxy_type=campaign.proxy_type,
            proxy_manager=proxy_manager,
            telegram_bot=telegram_bot,
            anti_detection=anti_detection,
            settings=settings
        )
        
        # Create campaign in database
        campaign_id = db.create_campaign(
            total=len(campaign.maillist),
            subject=campaign.subject
        )
        
        # Start sending in background
        asyncio.create_task(email_sender.start_sending(campaign_id))
        
        return JSONResponse({
            "status": "started",
            "campaign_id": campaign_id,
            "total_emails": len(campaign.maillist)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stop-campaign")
async def stop_campaign(campaign_id: int = Form(...)):
    """Stop active campaign"""
    global email_sender
    
    if email_sender:
        email_sender.stop()
        db.update_campaign_status(campaign_id, "stopped")
        
    return JSONResponse({"status": "stopped"})

@app.get("/api/status")
async def get_status():
    """Get current campaign status"""
    if email_sender:
        return JSONResponse(email_sender.get_status())
    return JSONResponse({"status": "idle"})

@app.get("/api/stats")
async def get_stats():
    """Get real-time statistics"""
    campaigns = db.get_all_campaigns()
    templates = db.get_all_templates()
    
    return JSONResponse({
        "campaigns": campaigns,
        "templates": len(templates),
        "total_sent": sum(c.get("sent", 0) for c in campaigns),
        "active": any(c.get("status") == "running" for c in campaigns)
    })

@app.post("/api/proxy/check")
async def check_proxies(proxies: ProxyCheck):
    """Check proxy list"""
    results = await proxy_manager.check_proxies(proxies.proxies)
    return JSONResponse({"results": results})

@app.post("/api/proxy/list")
async def upload_proxy_list(file: UploadFile = File(...)):
    """Upload proxy list file"""
    content = await file.read()
    proxies = content.decode().strip().split("\n")
    proxies = [p.strip() for p in proxies if p.strip()]
    
    proxy_manager.load_proxies(proxies)
    
    return JSONResponse({
        "status": "loaded",
        "count": len(proxies)
    })

@app.post("/api/filter/maillist")
async def filter_maillist(filter_data: MaillistFilter):
    """Filter maillist by domains"""
    results = {}
    
    for email in filter_data.emails:
        domain = email.split("@")[-1] if "@" in email else "unknown"
        
        if domain not in results:
            results[domain] = []
        results[domain].append(email)
    
    # Filter by requested domains
    filtered = {}
    for domain in filter_data.domains:
        domain = domain.strip().lower()
        for key, emails in results.items():
            if domain in key.lower():
                filtered[key] = {
                    "count": len(emails),
                    "emails": emails
                }
    
    return JSONResponse({"results": filtered})

@app.post("/api/templates/save")
async def save_template(template: TemplateSave):
    """Save email template"""
    template_id = db.save_template(
        name=template.name,
        content=template.content,
        content_type=template.content_type
    )
    
    return JSONResponse({
        "status": "saved",
        "template_id": template_id
    })

@app.get("/api/templates/list")
async def list_templates():
    """List all templates"""
    templates = db.get_all_templates()
    return JSONResponse({"templates": templates})

@app.post("/api/templates/load")
async def load_template(template_id: int = Form(...)):
    """Load a specific template"""
    template = db.get_template(template_id)
    
    if template:
        return JSONResponse({"template": template})
    raise HTTPException(status_code=404, detail="Template not found")

@app.delete("/api/templates/delete")
async def delete_template(template_id: int = Form(...)):
    """Delete a template"""
    db.delete_template(template_id)
    return JSONResponse({"status": "deleted"})

# === MAIN ===

def initialize_telegram():
    """Initialize Telegram bot"""
    global telegram_bot
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    user_id = os.getenv("TELEGRAM_USER_ID")
    
    if token and user_id and token != "your_bot_token_here":
        telegram_bot = TelegramBot(token, user_id)

if __name__ == "__main__":
    # Initialize database
    db.init_database()
    
    # Initialize Telegram
    initialize_telegram()
    
    # Get port from environment
    port = int(os.getenv("SERVER_PORT", "5000"))
    
    # Run server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )