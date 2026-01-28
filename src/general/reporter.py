"""
Reporter Agent - The Voice of Nexus Sovereign
Creates daily briefings from raw technical data in the ledger
Transforms code into professional intelligence reports
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class ReporterAgent:
    def __init__(self):
        self.agent_id = "reporter_001"
        self.agent_type = "intelligence"
        self.name = "Reporter"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
    def log(self, message):
        print(f"[{self.name}] {message}")
        
    def fetch_recent_activity(self, hours=24):
        """Get recent activity from the ledger"""
        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Get activity from last 24 hours
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            response = supabase.table("ledger")\
                .select("*")\
                .gte("created_at", cutoff_time)\
                .order("created_at", desc=True)\
                .execute()
                
            return response.data
            
        except Exception as e:
            self.log(f"ERROR fetching activity: {e}")
            return []
            
    def categorize_activity(self, entries):
        """Categorize ledger entries by type"""
        categories = {
            "security_alerts": [],
            "market_intelligence": [],
            "system_health": [],
            "planning": [],
            "research": []
        }
        
        for entry in entries:
            msg_type = entry.get("message_type", "")
            agent_type = entry.get("agent_type", "")
            
            if msg_type == "security_alert":
                categories["security_alerts"].append(entry)
            elif msg_type in ["scan_complete", "market_scan", "github_scan"]:
                categories["market_intelligence"].append(entry)
            elif msg_type in ["diagnostics_complete", "simulation_complete"]:
                categories["system_health"].append(entry)
            elif msg_type in ["plan_validation", "plan_approved"]:
                categories["planning"].append(entry)
            elif agent_type == "research":
                categories["research"].append(entry)
                
        return categories
        
    def generate_executive_summary(self, categories):
        """Create executive summary for stakeholders"""
        summary = []
        
        # Security section
        if categories["security_alerts"]:
            alerts = len(categories["security_alerts"])
            summary.append(f"SECURITY: {alerts} high-priority alerts detected in last 24h.")
            
        # Market intelligence
        if categories["market_intelligence"]:
            intel_count = len(categories["market_intelligence"])
            summary.append(f"INTELLIGENCE: {intel_count} new market signals processed.")
            
        # System health
        if categories["system_health"]:
            health_items = len(categories["system_health"])
            summary.append(f"SYSTEMS: {health_items} diagnostic cycles completed successfully.")
            
        # Planning
        if categories["planning"]:
            plans = len(categories["planning"])
            approved = sum(1 for p in categories["planning"] if p.get("payload", {}).get("verdict") == "APPROVED")
            rejected = sum(1 for p in categories["planning"] if p.get("payload", {}).get("verdict") == "REJECTED")
            summary.append(f"PLANNING: {plans} plans reviewed ({approved} approved, {rejected} rejected).")
            
        return summary
        
    def write_intelligence_briefing(self, summary, categories):
        """Write professional intelligence briefing to ledger"""
        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            briefing = {
                "timestamp": datetime.now().isoformat(),
                "period_covered": "24 hours",
                "executive_summary": summary,
                "detailed_categories": {
                    "total_entries": sum(len(entries) for entries in categories.values()),
                    "breakdown": {k: len(v) for k, v in categories.items()}
                },
                "key_findings": self.extract_key_findings(categories),
                "recommendations": self.generate_recommendations(categories)
            }
            
            data = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "message_type": "intelligence_briefing",
                "payload": briefing,
                "status": "published"
            }
            
            supabase.table("ledger").insert(data).execute()
            self.log("Intelligence briefing published")
            
        except Exception as e:
            self.log(f"ERROR writing briefing: {e}")
            
    def extract_key_findings(self, categories):
        """Extract key findings from categorized data"""
        findings = []
        
        # Security findings
        for alert in categories["security_alerts"]:
            payload = alert.get("payload", {})
            org = payload.get("org", "Unknown")
            keywords = payload.get("secret_keywords", [])
            if keywords:
                findings.append(f"Potential security exposure detected at {org}: {', '.join(keywords)}")
                
        # Market findings
        for intel in categories["market_intelligence"]:
            payload = intel.get("payload", {})
            if payload.get("return_pct"):
                findings.append(f"Market simulation shows {payload['return_pct']}% average return")
                
        return findings
        
    def generate_recommendations(self, categories):
        """Generate strategic recommendations"""
        recommendations = []
        
        # Security recommendations
        if categories["security_alerts"]:
            recommendations.append("Investigate security alerts immediately - potential data exposure detected")
            
        # System recommendations
        if len(categories["system_health"]) < 3:
            recommendations.append("Increase system monitoring frequency - reduced diagnostic coverage detected")
            
        # Planning recommendations
        if any(p.get("payload", {}).get("verdict") == "REJECTED" for p in categories["planning"]):
            recommendations.append("Review rejected plans - address high-risk factors before resubmission")
            
        return recommendations
        
    def run(self):
        """Generate daily intelligence briefing"""
        from datetime import timedelta
        
        self.log("="*60)
        self.log("NEXUS SOVEREIGN - DAILY INTELLIGENCE BRIEFING")
        self.log("="*60)
        
        # Fetch recent activity
        entries = self.fetch_recent_activity()
        self.log(f"Found {len(entries)} entries in last 24h")
        
        # Categorize
        categories = self.categorize_activity(entries)
        
        # Generate summary
        summary = self.generate_executive_summary(categories)
        
        # Display summary
        self.log("\nEXECUTIVE SUMMARY:")
        for line in summary:
            self.log(f"  • {line}")
            
        # Write briefing
        self.write_intelligence_briefing(summary, categories)
        
        # Display key findings
        findings = self.extract_key_findings(categories)
        if findings:
            self.log("\nKEY FINDINGS:")
            for finding in findings:
                self.log(f"  • {finding}")
                
        self.log("="*60)
        self.log("Briefing complete - check ledger for full report")
        self.log("="*60)

if __name__ == "__main__":
    reporter = ReporterAgent()
    reporter.run()