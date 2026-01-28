"""
Mode Manager - Controls system-wide operational modes
VIP uses this to switch between Money, Discovery, and Survivor modes
"""
import os
import sys
import time
import psutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class ModeManager:
    def __init__(self):
        self.name = "ModeManager"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.current_mode = "discovery"  # Default
        self.modes = {
            "money": self._enter_money_mode,
            "discovery": self._enter_discovery_mode,
            "survivor": self._enter_survivor_mode
        }
        
    def log(self, message):
        print(f"[{self.name}] {message}")
        
    def get_system_status(self):
        """Read current mode from database"""
        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            result = supabase.table("system_status")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
                
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            self.log(f"ERROR reading status: {e}")
            return None
            
    def set_mode(self, new_mode, reason=""):
        """Switch system to new mode"""
        if new_mode not in self.modes:
            self.log(f"ERROR: Unknown mode {new_mode}")
            return False
            
        self.log(f"="*50)
        self.log(f"MODE SWITCH: {self.current_mode} -> {new_mode}")
        if reason:
            self.log(f"REASON: {reason}")
        self.log(f"="*50)
        
        # Update database
        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            supabase.table("system_status").insert({
                "current_mode": new_mode,
                "agent_health": {"previous_mode": self.current_mode, "reason": reason},
                "system_load": psutil.cpu_percent(),
                "last_updated": datetime.now().isoformat()
            }).execute()
            
        except Exception as e:
            self.log(f"ERROR updating mode: {e}")
            return False
            
        # Execute mode transition
        self.current_mode = new_mode
        self.modes[new_mode]()
        
        return True
        
    def _enter_money_mode(self):
        """MONEY MODE: Focus all resources on profit"""
        self.log("ENTERING MONEY MODE")
        self.log("Actions:")
        self.log("  - Killing Discovery agents")
        self.log("  - Killing Learning agents")
        self.log("  - Spawning 5 Sniper Agents")
        self.log("  - Pulse: Stock tickers only")
        self.log("  - Simulator: Market prediction only")
        
        # Here you would call incubator to spawn/kill agents
        # For now, we log the intent
        
    def _enter_discovery_mode(self):
        """DISCOVERY MODE: Explore new opportunities"""
        self.log("ENTERING DISCOVERY MODE")
        self.log("Actions:")
        self.log("  - Activating Pioneer")
        self.log("  - Activating Asteroid Tracker")
        self.log("  - Pulse: Scientific patents & space telemetry")
        self.log("  - Spider: Research mode")
        
    def _enter_survivor_mode(self):
        """SURVIVOR MODE: System under attack, go stealth"""
        self.log("ENTERING SURVIVOR MODE")
        self.log("Actions:")
        self.log("  - All agents: 1% speed")
        self.log("  - Ghost headers activated")
        self.log("  - Pulse: Minimum viable queries")
        self.log("  - Survivor: Maximum logging")
        
    def check_auto_switch(self):
        """Auto-switch modes based on conditions"""
        cpu = psutil.cpu_percent()
        # TODO: Check for 429 errors, system health, etc.
        
        if cpu > 80:
            self.log(f"WARNING: High CPU ({cpu}%)")
            # Could auto-switch to survivor mode here
            
        return self.current_mode
        
    def run(self):
        """Test mode switching"""
        self.log("Mode Manager initialized")
        self.log(f"Current mode: {self.current_mode}")
        
        # Test switches
        time.sleep(2)
        self.set_mode("money", "High volatility detected")
        
        time.sleep(2)
        self.set_mode("discovery", "Market closed, researching")
        
        time.sleep(2)
        self.set_mode("survivor", "429 errors detected, stealth mode")

if __name__ == "__main__":
    manager = ModeManager()
    manager.run()