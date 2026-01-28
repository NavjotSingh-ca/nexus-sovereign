"""
Simulator - Runs 10,000 "What-If" market scenarios
Uses parallel processing for Stockfish-level speed
"""
import os
import sys
import json
import random
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class MarketSimulator:
    def __init__(self):
        self.name = "Simulator"
        self.agent_id = "simulator_001"
        self.agent_type = "simulator"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
    def log(self, message):
        print(f"[{self.name}] {message}")
        
    def write_to_ledger(self, message_type, payload):
        """Write results to ledger"""
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
            self.log(f"Results written to ledger")
            
        except Exception as e:
            self.log(f"ERROR: {e}")
            
    def run_scenario(self, scenario_id):
        """Run a single simulation scenario"""
        # Simulate market conditions
        initial_price = random.uniform(100, 500)
        volatility = random.uniform(0.01, 0.05)
        days = 30
        
        price = initial_price
        prices = [price]
        
        for day in range(days):
            change = random.gauss(0, volatility)
            price = price * (1 + change)
            prices.append(price)
            
        final_price = prices[-1]
        return {
            "scenario_id": scenario_id,
            "initial": round(initial_price, 2),
            "final": round(final_price, 2),
            "return_pct": round((final_price - initial_price) / initial_price * 100, 2),
            "max_drawdown": round(min((p - max(prices[:i+1])) / max(prices[:i+1]) * 100 
                                   for i, p in enumerate(prices) if i > 0), 2),
            "volatility": round(volatility * 100, 2)
        }
        
    def run_batch(self, num_scenarios=1000, max_workers=4):
        """Run multiple scenarios in parallel"""
        self.log(f"Starting {num_scenarios} simulations...")
        self.log(f"Using {max_workers} parallel workers")
        
        start_time = time.time()
        results = []
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.run_scenario, i): i 
                for i in range(num_scenarios)
            }
            
            completed = 0
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if completed % 100 == 0:
                        self.log(f"Progress: {completed}/{num_scenarios}")
                        
                except Exception as e:
                    self.log(f"Scenario failed: {e}")
                    
        elapsed = time.time() - start_time
        
        # Analyze results
        returns = [r["return_pct"] for r in results]
        analysis = {
            "total_scenarios": num_scenarios,
            "execution_time": round(elapsed, 2),
            "scenarios_per_second": round(num_scenarios / elapsed, 2),
            "avg_return": round(sum(returns) / len(returns), 2),
            "best_case": round(max(returns), 2),
            "worst_case": round(min(returns), 2),
            "profitable_pct": round(sum(1 for r in returns if r > 0) / len(returns) * 100, 2),
            "sample_results": results[:5]  # First 5 only
        }
        
        self.log(f"Simulation complete in {elapsed:.2f}s")
        self.log(f"Average return: {analysis['avg_return']}%")
        self.log(f"Best case: {analysis['best_case']}%")
        self.log(f"Worst case: {analysis['worst_case']}%")
        
        return analysis
        
    def run(self, num_scenarios=1000):
        """Main entry point"""
        self.log("="*50)
        self.log("MARKET SIMULATOR v1.0")
        self.log("="*50)
        
        results = self.run_batch(num_scenarios)
        self.write_to_ledger("simulation_complete", results)
        
        self.log("="*50)
        return results

if __name__ == "__main__":
    sim = MarketSimulator()
    sim.run(num_scenarios=1000)  # Run 1000 scenarios