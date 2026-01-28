"""
Base Worker - All workers inherit from this
Provides ledger writing and logging capabilities
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class BaseWorker:
    def __init__(self, agent_id, agent_type):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
    def log(self, message):
        """Print to console with agent ID"""
        print(f"[{self.agent_id}] {message}")
        
    def write_to_ledger(self, message_type, payload):
        """Write entry to Supabase ledger"""
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
            
    def check_kill_signal(self):
        """Check if VIP has issued shutdown command"""
        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Check for shutdown signal in last 60 seconds
            result = supabase.table("ledger")\
                .select("*")\
                .eq("agent_id", "VIP")\
                .eq("message_type", "SHUTDOWN")\
                .gte("created_at", (datetime.now().timestamp() - 60))\
                .execute()
                
            return len(result.data) > 0
            
        except:
            return False
            
    def execute(self):
        """Override this in subclass"""
        raise NotImplementedError("Subclasses must implement execute()")