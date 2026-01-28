"""
VIP Supervisor - The Central Brain of Nexus Sovereign
Level 0: Manages system health, budget ($0), and API limits
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class VIPSupervisor:
    def __init__(self):
        self.name = "VIP_Supervisor"
        self.status = "INITIALIZING"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
    def check_environment(self):
        """Verify all required components are present"""
        print(f"[{self.name}] Checking environment...")
        
        # Check Python version
        version = sys.version_info
        print(f"[{self.name}] Python {version.major}.{version.minor}.{version.micro}")
        
        # Check environment variables
        if not self.supabase_url:
            print(f"[{self.name}] ERROR: SUPABASE_URL not found")
            return False
        if not self.supabase_key:
            print(f"[{self.name}] ERROR: SUPABASE_KEY not found")
            return False
            
        print(f"[{self.name}] Environment variables loaded")
        return True
        
    def check_database(self):
        """Test connection to Supabase Ledger"""
        try:
            from supabase import create_client
            
            print(f"[{self.name}] Connecting to Ledger...")
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Test query - count rows in ledger
            response = supabase.table("ledger").select("*", count="exact").limit(0).execute()
            count = response.count if hasattr(response, 'count') else 'unknown'
            
            print(f"[{self.name}] Ledger connection successful")
            print(f"[{self.name}] Current ledger entries: {count}")
            self.status = "ACTIVE"
            return True
            
        except Exception as e:
            print(f"[{self.name}] ERROR: Cannot connect to Ledger: {e}")
            return False
            
    def run_diagnostics(self):
        """Full system check"""
        print(f"\n{'='*50}")
        print(f"NEXUS SOVEREIGN - VIP SUPERVISOR")
        print(f"{'='*50}\n")
        
        env_ok = self.check_environment()
        if not env_ok:
            print(f"[{self.name}] DIAGNOSTICS FAILED - Environment")
            return False
            
        db_ok = self.check_database()
        if not db_ok:
            print(f"[{self.name}] DIAGNOSTICS FAILED - Database")
            return False
            
        print(f"\n{'='*50}")
        print(f"SYSTEM STATUS: {self.status}")
        print(f"{'='*50}\n")
        return True

if __name__ == "__main__":
    vip = VIPSupervisor()
    success = vip.run_diagnostics()
    
    if success:
        print("VIP Supervisor is ready. The Nexus is online.")
        sys.exit(0)
    else:
        print("VIP Supervisor failed to initialize. Check errors above.")
        sys.exit(1)