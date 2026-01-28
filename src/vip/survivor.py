"""
Survivor Organ - Black Box Logger
Records all system events locally for debugging and recovery
"""
import json
import os
from datetime import datetime
from pathlib import Path

class SurvivorOrgan:
    def __init__(self):
        self.log_dir = Path(__file__).parent.parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"survivor_{datetime.now().strftime('%Y%m%d')}.log"
        
    def log(self, level, agent, message, data=None):
        """Write a log entry"""
        timestamp = datetime.now().isoformat()
        
        entry = {
            "timestamp": timestamp,
            "level": level,
            "agent": agent,
            "message": message,
            "data": data
        }
        
        # Write to file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        # Also print to console
        print(f"[SURVIVOR] [{level}] {agent}: {message}")
        
    def info(self, agent, message, data=None):
        self.log("INFO", agent, message, data)
        
    def error(self, agent, message, data=None):
        self.log("ERROR", agent, message, data)
        
    def warning(self, agent, message, data=None):
        self.log("WARNING", agent, message, data)

if __name__ == "__main__":
    # Test the survivor
    survivor = SurvivorOrgan()
    survivor.info("VIP", "System initialized")
    survivor.info("Spider", "Scan completed", {"url": "example.com"})
    print(f"\nLog saved to: {survivor.log_file}")