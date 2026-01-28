"""
Ghost-Commit Agent - Watches GitHub for secret dev updates
The Hunter: Tracks commits in major tech repositories
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime
import random
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class GhostCommitAgent:
    def __init__(self):
        self.agent_id = "ghost_commit_001"
        self.agent_type = "hunter"
        self.name = "Ghost-Commit"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Target repositories (major tech companies)
        self.targets = [
            "microsoft",
            "google", 
            "apple",
            "amazon",
            "meta",
            "openai",
            "anthropics"
        ]
        
    def log(self, message):
        print(f"[{self.name}] {message}")
        
    def write_to_ledger(self, message_type, payload):
        """Write findings to ledger"""
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
            
            supabase.table("ledger").insert(data).execute()
            self.log(f"Written to ledger: {message_type}")
            
        except Exception as e:
            self.log(f"ERROR: {e}")
            
    def scan_github(self, org):
        """Simulate scanning GitHub for an organization"""
        self.log(f"Scanning {org}...")
        
        # Simulate API call delay
        time.sleep(1)
        
        # Simulate findings (in real version, use GitHub API)
        findings = {
            "org": org,
            "timestamp": datetime.now().isoformat(),
            "new_repos": random.randint(0, 3),
            "secret_keywords": [],
            "suspicious_commits": []
        }
        
        # Simulate finding something interesting
        
        if random.random() > 0.7:  # 30% chance of finding something
            keywords = ["api-key", "password", "secret", "token", "internal"]
            findings["secret_keywords"] = random.sample(keywords, k=random.randint(1, 2))
            findings["alert_level"] = "HIGH"
            self.log(f"!!! ALERT: Potential secrets found in {org} !!!")
        else:
            findings["alert_level"] = "LOW"
            
        return findings
        
    def run(self):
        """Main execution"""
        import random
        
        self.log("="*50)
        self.log("GHOST-COMMIT AGENT ACTIVATED")
        self.log("Hunting for secret dev updates...")
        self.log("="*50)
        
        all_findings = []
        
        for target in self.targets:
            result = self.scan_github(target)
            all_findings.append(result)
            
            if result.get("alert_level") == "HIGH":
                # Immediate alert
                self.write_to_ledger("security_alert", result)
            else:
                self.write_to_ledger("github_scan", result)
                
        # Summary report
        high_alerts = sum(1 for f in all_findings if f.get("alert_level") == "HIGH")
        self.log("="*50)
        self.log(f"Scan complete: {len(all_findings)} orgs scanned")
        self.log(f"High alerts: {high_alerts}")
        self.log("="*50)

if __name__ == "__main__":
    ghost = GhostCommitAgent()
    ghost.run()