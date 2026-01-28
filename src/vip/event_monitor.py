"""
Event Monitor - Watches ledger for events and triggers responses
Implements "if X finds Y, spawn Z" logic
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import the incubator
sys.path.insert(0, str(Path(__file__).parent.parent))
from vip.incubator import Incubator

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class EventMonitor:
    def __init__(self):
        self.name = "EventMonitor"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.incubator = Incubator()
        self.last_check = datetime.now()
        
    def log(self, message):
        print(f"[{self.name}] {message}")
        
    def check_new_events(self):
        """Check ledger for new events since last check"""
        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Get events since last check
            response = supabase.table("ledger")\
                .select("*")\
                .gte("created_at", self.last_check.isoformat())\
                .order("created_at", desc=True)\
                .execute()
                
            return response.data
            
        except Exception as e:
            self.log(f"ERROR checking events: {e}")
            return []
            
    def process_event(self, entry):
        """Process a single event and trigger responses"""
        msg_type = entry.get("message_type", "")
        agent_id = entry.get("agent_id", "")
        payload = entry.get("payload", {})
        
        self.log(f"Processing event: {msg_type} from {agent_id}")
        
        # Event-driven responses
        responses = []
        
        # Security alerts from Ghost-Commit
        if msg_type == "security_alert" and "ghost_commit" in agent_id:
            if self.incubator.handle_event("security_alert", payload):
                responses.append("security_response")
                
        # High volatility from market scans
        elif msg_type == "pulse_scan" and "pulse" in agent_id:
            if payload.get("return_pct", 0) > 10:
                if self.incubator.handle_event("market_scan", payload):
                    responses.append("volatility_response")
                    
        # Plan rejections from Inquisitor
        elif msg_type == "plan_validation" and "inquisitor" in agent_id:
            if payload.get("verdict") == "REJECTED":
                if self.incubator.handle_event("plan_rejected", payload):
                    responses.append("plan_response")
                    
        # Multiple new repos from GitHub scans
        elif msg_type == "github_scan" and "ghost_commit" in agent_id:
            if payload.get("new_repos", 0) > 2:
                if self.incubator.handle_event("github_scan", payload):
                    responses.append("github_response")
                    
        return responses
        
    def run_monitor(self, duration_minutes=5):
        """Run event monitor for specified duration"""
        self.log("="*50)
        self.log("EVENT MONITOR - INTELLIGENCE SYNTHESIS")
        self.log("="*50)
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            self.log(f"Checking for new events (last check: {self.last_check})")
            
            # Check for new events
            events = self.check_new_events()
            
            if events:
                self.log(f"Found {len(events)} new events")
                
                # Process each event
                for event in events:
                    responses = self.process_event(event)
                    
                    if responses:
                        self.log(f"Triggered responses: {responses}")
                        
            else:
                self.log("No new events found")
                
            # Update last check time
            self.last_check = datetime.now()
            
            # Wait before next check
            self.log("Waiting 30 seconds before next check...")
            time.sleep(30)
            
        self.log("Monitor cycle complete")

if __name__ == "__main__":
    monitor = EventMonitor()
    monitor.run_monitor(duration_minutes=2)  # Run for 2 minutes