"""
The General - Central Brain of Nexus Sovereign
Coordinates VIP, Workers, and Ledger communication
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from vip.supervisor import VIPSupervisor
from vip.survivor import SurvivorOrgan
from workers.spider import SpiderWorker

class General:
    def __init__(self):
        self.name = "General"
        self.vip = VIPSupervisor()
        self.survivor = SurvivorOrgan()
        self.workers = {}
        
    def initialize(self):
        """Boot sequence"""
        print(f"\n{'='*60}")
        print(f"NEXUS SOVEREIGN - SYSTEM BOOT")
        print(f"{'='*60}\n")
        
        # Start VIP
        self.survivor.info(self.name, "Initializing VIP Supervisor")
        if not self.vip.run_diagnostics():
            self.survivor.error(self.name, "VIP initialization failed")
            return False
            
        self.survivor.info(self.name, "VIP online")
        return True
        
    def register_worker(self, worker_class, worker_id):
        """Add a worker to the swarm"""
        worker = worker_class()
        self.workers[worker_id] = worker
        self.survivor.info(self.name, f"Registered worker: {worker_id}")
        return worker
        
    def dispatch_task(self, worker_id, task_func, *args):
        """Send command to a worker"""
        if worker_id not in self.workers:
            self.survivor.error(self.name, f"Worker not found: {worker_id}")
            return None
            
        worker = self.workers[worker_id]
        self.survivor.info(self.name, f"Dispatching task to {worker_id}")
        
        try:
            result = task_func(*args)
            self.survivor.info(self.name, f"Task completed by {worker_id}")
            return result
        except Exception as e:
            self.survivor.error(self.name, f"Task failed: {e}")
            return None
            
    def read_ledger(self):
        """Check the ledger for new messages"""
        try:
            from supabase import create_client
            supabase = create_client(self.vip.supabase_url, self.vip.supabase_key)
            
            response = supabase.table("ledger").select("*").order("created_at", desc=True).limit(5).execute()
            return response.data
        except Exception as e:
            self.survivor.error(self.name, f"Cannot read ledger: {e}")
            return []
            
    def run_cycle(self):
        """One operational cycle"""
        print(f"\n[{self.name}] Running operational cycle...")
        
        # Read recent ledger entries
        entries = self.read_ledger()
        print(f"[{self.name}] Ledger entries found: {len(entries)}")
        
        for entry in entries:
            print(f"  - {entry['agent_id']}: {entry['message_type']}")
            
        return True
        
    def shutdown(self):
        """Graceful shutdown"""
        self.survivor.info(self.name, "System shutdown initiated")
        print(f"\n{'='*60}")
        print(f"NEXUS SOVEREIGN - OFFLINE")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    general = General()
    
    # Initialize
    if not general.initialize():
        print("System boot failed")
        sys.exit(1)
        
    # Register workers
    general.register_worker(SpiderWorker, "spider_001")
    
    # Run a cycle
    general.run_cycle()
    
    # Shutdown
    general.shutdown()