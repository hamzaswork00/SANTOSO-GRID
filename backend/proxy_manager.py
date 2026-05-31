"""
SANTOSO-GRID - Proxy Manager
Load, check, and rotate proxies
Version: 1.0
"""

import asyncio
import socket
from typing import List, Dict, Optional
from pathlib import Path

class ProxyManager:
    """Manage proxy list and rotation"""
    
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.current_proxy_index = 0
        self.proxy_type = None
        
    def load_proxies(self, proxy_list: List[str]):
        """Load proxies from list"""
        self.proxies = []
        
        for line in proxy_list:
            line = line.strip()
            if not line:
                continue
            
            # Parse proxy format
            try:
                # Format: ip:port or ip:port:user:pass
                parts = line.split(":")
                
                if len(parts) >= 2:
                    proxy = {
                        "host": parts[0],
                        "port": int(parts[1]),
                        "full": line
                    }
                    
                    if len(parts) == 4:
                        proxy["user"] = parts[2]
                        proxy["pass"] = parts[3]
                    
                    # Detect type
                    proxy["type"] = self.detect_proxy_type(line)
                    
                    self.proxies.append(proxy)
                    
            except Exception as e:
                print(f"Error parsing proxy {line}: {e}")
        
        print(f"Loaded {len(self.proxies)} proxies")
    
    def detect_proxy_type(self, proxy_line: str) -> str:
        """Detect proxy type from line"""
        proxy_line = proxy_line.lower()
        
        if "socks5" in proxy_line or proxy_line.startswith("socks5"):
            return "socks5"
        elif "socks4" in proxy_line or proxy_line.startswith("socks4"):
            return "socks4"
        elif "http" in proxy_line:
            return "http"
        else:
            return "http"
    
    async def check_proxies(self, proxy_list: List[str] = None) -> List[Dict]:
        """Check proxy connectivity"""
        proxies_to_check = proxy_list if proxy_list else [p["full"] for p in self.proxies]
        
        results = []
        
        for proxy_line in proxies_to_check:
            result = {
                "proxy": proxy_line,
                "status": "dead",
                "type": self.detect_proxy_type(proxy_line),
                "response_time": 0
            }
            
            try:
                parts = proxy_line.split(":")
                host = parts[0]
                port = int(parts[1])
                
                # Test connection
                start = asyncio.get_event_loop().time()
                
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=5
                )
                
                writer.close()
                await writer.wait_closed()
                
                end = asyncio.get_event_loop().time()
                response_time = int((end - start) * 1000)
                
                result["status"] = "live"
                result["response_time"] = response_time
                
            except Exception as e:
                result["status"] = "dead"
            
            results.append(result)
        
        # Update working proxies
        self.working_proxies = [r for r in results if r["status"] == "live"]
        
        return results
    
    async def check_single_proxy(self, host: str, port: int) -> bool:
        """Check a single proxy"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=5
            )
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False
    
    def get_current_proxy(self) -> Optional[Dict]:
        """Get current proxy for rotation"""
        if not self.working_proxies:
            return None
        
        proxy = self.working_proxies[self.current_proxy_index]
        return proxy
    
    def rotate_proxy(self):
        """Rotate to next proxy"""
        if self.working_proxies:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.working_proxies)
    
    def get_proxy_count(self) -> int:
        """Get total proxy count"""
        return len(self.proxies)
    
    def get_working_count(self) -> int:
        """Get working proxy count"""
        return len(self.working_proxies)