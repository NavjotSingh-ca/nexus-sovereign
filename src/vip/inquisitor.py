"""
Inquisitor - Red Team Agent
Challenges the General's plans to find flaws before execution
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class Inquisitor:
    def __init__(self):
        self.agent_id = "inquisitor_001"
        self.agent_type = "validator"
        self.name = "Inquisitor"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
    def log(self, message):
        print(f"[{self.name}] {message}")
        
    def write_to_ledger(self, message_type, payload):
        """Write challenge results to ledger"""
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
            
    def challenge_plan(self, plan):
        """Analyze a plan and find 3 reasons it might fail"""
        self.log("="*50)
        self.log(f"CHALLENGING PLAN: {plan.get('name', 'Unnamed')}")
        self.log("="*50)
        
        challenges = []
        
        # Challenge 1: Data Quality
        if not plan.get('data_verified'):
            challenges.append({
                "id": 1,
                "category": "DATA",
                "challenge": "Source data has not been independently verified",
                "risk": "High",
                "recommendation": "Cross-reference with secondary sources"
            })
            
        # Challenge 2: Assumptions
        if plan.get('assumptions', 0) > 3:
            challenges.append({
                "id": 2,
                "category": "ASSUMPTIONS",
                "challenge": f"Plan relies on {plan.get('assumptions')} unproven assumptions",
                "risk": "Medium",
                "recommendation": "Validate core assumptions with small test"
            })
            
        # Challenge 3: Resource Constraints
        if plan.get('budget', 0) > 1000:
            challenges.append({
                "id": 3,
                "category": "BUDGET",
                "challenge": f"Budget ${plan.get('budget')} exceeds safe operational threshold",
                "risk": "High",
                "recommendation": "Request VIP approval or reduce scope"
            })
            
        # Challenge 4: Timing
        if plan.get('timeframe', 'unknown') == 'immediate':
            challenges.append({
                "id": 4,
                "category": "TIMING",
                "challenge": "Immediate execution leaves no room for error correction",
                "risk": "Medium",
                "recommendation": "Add 24-hour observation period"
            })
            
        # If no challenges found, create generic ones
        if len(challenges) < 3:
            challenges.append({
                "id": len(challenges)+1,
                "category": "UNKNOWN",
                "challenge": "Black swan events not accounted for",
                "risk": "Unknown",
                "recommendation": "Build contingency protocols"
            })
            
        # Display challenges
        for c in challenges[:3]:  # Only top 3
            self.log(f"\nCHALLENGE #{c['id']} [{c['category']}]")
            self.log(f"  Issue: {c['challenge']}")
            self.log(f"  Risk: {c['risk']}")
            self.log(f"  Fix: {c['recommendation']}")
            
        # Verdict
        high_risks = sum(1 for c in challenges if c['risk'] == 'High')
        
        if high_risks >= 2:
            verdict = "REJECTED"
            self.log(f"\n!!! VERDICT: {verdict} !!!")
            self.log("Plan has too many critical flaws")
        elif high_risks == 1:
            verdict = "CONDITIONAL"
            self.log(f"\nVERDICT: {verdict}")
            self.log("Address high-risk issue before proceeding")
        else:
            verdict = "APPROVED"
            self.log(f"\nVERDICT: {verdict}")
            self.log("Plan passes initial scrutiny")
            
        # Write to ledger
        result = {
            "plan_name": plan.get('name'),
            "timestamp": datetime.now().isoformat(),
            "challenges": challenges[:3],
            "verdict": verdict,
            "high_risk_count": high_risks
        }
        
        self.write_to_ledger("plan_validation", result)
        
        self.log("="*50)
        return verdict, challenges[:3]
        
    def run_test(self):
        """Test with sample plans"""
        test_plans = [
            {
                "name": "Aggressive Market Entry",
                "data_verified": False,
                "assumptions": 5,
                "budget": 5000,
                "timeframe": "immediate"
            },
            {
                "name": "Conservative Research",
                "data_verified": True,
                "assumptions": 2,
                "budget": 100,
                "timeframe": "gradual"
            }
        ]
        
        for plan in test_plans:
            self.challenge_plan(plan)
            print("\n")

if __name__ == "__main__":
    inquisitor = Inquisitor()
    inquisitor.run_test()