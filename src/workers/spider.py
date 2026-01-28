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
        """Simulate scanning a website"""
        if not self.running:
            return None
            
        self.log(f"Scanning: {url}")
        time.sleep(1)
        
        report = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status": "scanned",
            "findings": ["header_collected", "links_found"],
            "data_size": 1024
        }
        
        self.write_to_ledger("scan_complete", report)
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
                test_url = "https://example.com"
                result = self.scan_target(test_url)
                
                if not self.running:
                    break
                    
                self.log("Task complete. Waiting 30s before next scan...")
                time.sleep(30)
                
        except KeyboardInterrupt:
            self.log("Interrupted by user")
        finally:
            self.running = False
            self.log("Worker stopped")

if __name__ == "__main__":
    spider = SpiderWorker()
    spider.run()