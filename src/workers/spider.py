"""
Spider Worker - Web scraping agent with kill-signal listener
Level 2: Specialized organ for data collection
"""
import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class SpiderWorker:
    def __init__(self):
        self.agent_id = "spider_001"
        self.agent_type = "worker"
        self.name = "Spider"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.running = True
        self.kill_check_interval = 60  # Check every 60 seconds
        
    def log(self, message):
        print(f"[{self.name}] {message}")
        
    def check_kill_signal(self):
        """Check if VIP has issued shutdown command - runs every 60s"""
        while self.running:
            try:
                from supabase import create_client
                supabase = create_client(self.supabase_url, self.supabase_key)
                
                # Check for SHUTDOWN signal from VIP in last 2 minutes
                result = supabase.table("ledger")\
                    .select("*")\
                    .eq("agent_id", "VIP")\
                    .eq("message_type", "SHUTDOWN")\
                    .eq("status", "active")\
                    .execute()
                    
                if len(result.data) > 0:
                    self.log("!!! KILL SIGNAL RECEIVED FROM VIP !!!")
                    self.log("Shutting down immediately...")
                    self.running = False
                    sys.exit(0)
                    
            except Exception as e:
                pass  # Silent fail, retry next cycle
                
            # Wait 60 seconds before next check
            time.sleep(self.kill_check_interval)
            
    def write_to_ledger(self, message_type, payload):
        """Write a message to the central ledger"""
        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            data = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "message_type": message_type,
                "payload": payload,
                "status": "pending"
            }
            
            result = supabase.table("ledger").insert(data).execute()
            self.log(f"Written to ledger: {message_type}")
            return True
            
        except Exception as e:
            self.log(f"ERROR writing to ledger: {e}")
            return False
            
    def scan_target(self, url):
        """Actually scrape real websites"""
        self.log(f"REAL SCAN: {url}")
        
        try:
            # Real HTTP request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            # Parse real HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract real data
            title = soup.find('title').get_text() if soup.find('title') else 'No title'
            links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
            images = len(soup.find_all('img'))
            text_length = len(soup.get_text())
            
            # Check for real security issues
            security_findings = []
            if 'api-key' in response.text.lower():
                security_findings.append('api_key_exposed')
            if 'password' in response.text.lower():
                security_findings.append('password_mentioned')
            if 'internal' in response.text.lower():
                security_findings.append('internal_reference')
                
            report = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "title": title,
                "links_found": len(links),
                "images_found": images,
                "text_length": text_length,
                "security_findings": security_findings,
                "http_status": response.status_code
            }
            
            self.log(f"Found: {title} | {len(links)} links | {len(security_findings)} security issues")
            
        except Exception as e:
            report = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
                "security_findings": []
            }
            self.log(f"Scan failed: {e}")
            
        self.write_to_ledger("real_scan_complete", report)
        return report
        
    def run(self):
        """Main execution with kill-signal listener"""
        self.log("Worker starting...")
        self.log("Kill-signal listener active (checking every 60s)")
        
        # Start kill-signal checker in background thread
        kill_thread = threading.Thread(target=self.check_kill_signal, daemon=True)
        kill_thread.start()
        
        # Main work loop
        try:
            while self.running:
                # Real targets to scan
                test_urls = [
                    "https://news.ycombinator.com",      # Hacker News
                    "https://techcrunch.com",            # Tech news
                    "https://arstechnica.com",           # Tech/security news
                    "https://github.com/microsoft",      # Microsoft's GitHub
                    "https://blog.google"                # Google blog
                ]
                
                for url in test_urls:
                    if not self.running:
                        break
                    result = self.scan_target(url)
                    self.log(f"Task complete. Waiting 30s before next scan...")
                    time.sleep(30)
                
        except KeyboardInterrupt:
            self.log("Interrupted by user")
        finally:
            self.running = False
            self.log("Worker stopped")

if __name__ == "__main__":
    spider = SpiderWorker()
    spider.run()