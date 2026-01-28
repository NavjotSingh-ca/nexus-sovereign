"""
Incubator - Dynamic Worker Spawner
Creates temporary agents on demand, executes them, then cleans up
"""
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class Incubator:
    def __init__(self):
        self.name = "Incubator"
        self.temp_dir = Path(__file__).parent.parent.parent / "temp_agents"
        self.temp_dir.mkdir(exist_ok=True)
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
    def create_worker_template(self, task_type, task_params):
        """Generate Python code for a temporary worker"""
        
        templates = {
            "geologist": self._geologist_template,
            "legal_auditor": self._legal_auditor_template,
            "market_scanner": self._market_scanner_template,
            "custom": self._custom_template
        }
        
        if task_type not in templates:
            return None
            
        return templates[task_type](task_params)
        
    def _geologist_template(self, params):
        """Template for mining/resource research"""
        return f'''
import sys
sys.path.insert(0, r"{Path(__file__).parent.parent}")
from workers.base_worker import BaseWorker

class TempGeologist(BaseWorker):
    def __init__(self):
        super().__init__("temp_geologist", "geologist")
        self.resource = "{params.get('resource', 'lithium')}"
        self.location = "{params.get('location', 'Chile')}"
        
    def execute(self):
        self.log(f"Researching {{self.resource}} in {{self.location}}")
        # Simulate research
        import time
        time.sleep(2)
        
        findings = {{
            "resource": self.resource,
            "location": self.location,
            "reserves": "High",
            "extraction_cost": "$3,200/ton",
            "regulatory_status": "Permits required"
        }}
        
        self.write_to_ledger("geology_report", findings)
        self.log("Task complete")
        return findings

if __name__ == "__main__":
    agent = TempGeologist()
    agent.execute()
'''
    
    def _legal_auditor_template(self, params):
        """Template for legal research"""
        return f'''
import sys
sys.path.insert(0, r"{Path(__file__).parent.parent}")
from workers.base_worker import BaseWorker

class TempLegalAuditor(BaseWorker):
    def __init__(self):
        super().__init__("temp_legal", "legal_auditor")
        self.topic = "{params.get('topic', 'mining_law')}"
        self.jurisdiction = "{params.get('jurisdiction', 'Chile')}"
        
    def execute(self):
        self.log(f"Auditing {{self.topic}} in {{self.jurisdiction}}")
        import time
        time.sleep(2)
        
        findings = {{
            "topic": self.topic,
            "jurisdiction": self.jurisdiction,
            "compliance_required": True,
            "key_statutes": ["Law 18.248", "Decree 132"],
            "risk_level": "Medium"
        }}
        
        self.write_to_ledger("legal_report", findings)
        self.log("Task complete")
        return findings

if __name__ == "__main__":
    agent = TempLegalAuditor()
    agent.execute()
'''
    
    def _market_scanner_template(self, params):
        """Template for rapid market analysis"""
        return f'''
import sys
sys.path.insert(0, r"{Path(__file__).parent.parent}")
from workers.base_worker import BaseWorker

class TempMarketScanner(BaseWorker):
    def __init__(self):
        super().__init__("temp_market", "market_scanner")
        self.symbol = "{params.get('symbol', 'BTC')}"
        
    def execute(self):
        self.log(f"Scanning market for {{self.symbol}}")
        import time
        time.sleep(1)
        
        data = {{
            "symbol": self.symbol,
            "price": 42000,
            "trend": "bullish",
            "volume": "high"
        }}
        
        self.write_to_ledger("market_scan", data)
        self.log("Task complete")
        return data

if __name__ == "__main__":
    agent = TempMarketScanner()
    agent.execute()
'''
    
    def _custom_template(self, params):
        """Custom template for unique tasks"""
        code = params.get('code', '')
        return code
        
    def spawn(self, task_type, task_params, timeout=30):
        """Create, execute, and destroy a temporary worker"""
        print(f"[{self.name}] Spawning {task_type} agent...")
        
        # Generate code
        code = self.create_worker_template(task_type, task_params)
        if not code:
            print(f"[{self.name}] ERROR: Unknown template {task_type}")
            return None
            
        # Write to temp file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = self.temp_dir / f"temp_{task_type}_{timestamp}.py"
        
        with open(temp_file, "w") as f:
            f.write(code)
            
        print(f"[{self.name}] Temp file created: {temp_file.name}")
        
        # Execute
        try:
            result = subprocess.run(
                [sys.executable, str(temp_file)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            print(f"[{self.name}] Output:\n{result.stdout}")
            if result.stderr:
                print(f"[{self.name}] Errors:\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"[{self.name}] ERROR: Agent timed out after {timeout}s")
        except Exception as e:
            print(f"[{self.name}] ERROR: {e}")
            
        # Cleanup
        finally:
            if temp_file.exists():
                temp_file.unlink()
                print(f"[{self.name}] Temp file deleted")
                
        print(f"[{self.name}] Spawn cycle complete")
        return True
        
    def handle_event(self, trigger_event, event_data):
        """Event-driven spawning - if X finds Y, spawn Z"""
        self.log(f"Handling event: {trigger_event}")
        
        # Event mapping: trigger → response agents
        event_map = {
            "security_alert": {
                "condition": lambda data: len(data.get("secret_keywords", [])) > 0,
                "spawn": ["investigator", "counter_intel"],
                "reason": "Security exposure detected"
            },
            "github_scan": {
                "condition": lambda data: data.get("new_repos", 0) > 2,
                "spawn": ["repo_analyzer", "code_scanner"],
                "reason": "Multiple new repositories detected"
            },
            "market_scan": {
                "condition": lambda data: abs(data.get("return_pct", 0)) > 10,
                "spawn": ["volatility_analyzer", "risk_assessor"],
                "reason": "High volatility detected"
            },
            "plan_rejected": {
                "condition": lambda data: data.get("verdict") == "REJECTED",
                "spawn": ["plan_optimizer", "risk_mitigator"],
                "reason": "Plan rejected by Inquisitor"
            }
        }
        
        if trigger_event in event_map:
            rule = event_map[trigger_event]
            
            if rule["condition"](event_data):
                self.log(f"Event conditions met - spawning response agents")
                
                for agent_type in rule["spawn"]:
                    self.log(f"Spawning {agent_type} in response to {trigger_event}")
                    
                    # Create response agent
                    self.spawn(agent_type, {
                        "trigger_event": trigger_event,
                        "trigger_data": event_data,
                        "mission": rule["reason"]
                    }, timeout=60)
                    
                return True
                
        self.log("No event conditions triggered")
        return False

if __name__ == "__main__":
    # Test the incubator
    incubator = Incubator()
    
    # Spawn a geologist
    incubator.spawn("geologist", {
        "resource": "lithium",
        "location": "Chile"
    })
    
    # Spawn a legal auditor
    incubator.spawn("legal_auditor", {
        "topic": "environmental_law",
        "jurisdiction": "Argentina"
    })