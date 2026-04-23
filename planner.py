"""
SRIE Planner v0.1
Action Planning Module

Reads Introspection Reports and generates executable action plans.
"""

import os
import sys
import json
from datetime import datetime

# 配置项
CONFIDENCE_THRESHOLD = 0.6

class Planner:
    def __init__(self, report_path=None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.report = self._load_report(report_path)
        self.plan = {
            "plan_id": datetime.now().strftime("PLAN-%Y%m%d-%H%M%S"),
            "generated_at": datetime.now().isoformat(),
            "actions": []
        }
        
    def _load_report(self, path):
        if not path:
            # Auto-detect latest log in ./logs/
            logs_dir = os.path.join(self.base_dir, "logs")
            if not os.path.exists(logs_dir):
                raise FileNotFoundError("Logs directory not found. Run introspector.py first.")
            files = sorted(os.listdir(logs_dir), reverse=True)
            json_files = [f for f in files if f.endswith('.json')]
            if not json_files:
                raise FileNotFoundError("No introspection reports found.")
            path = os.path.join(logs_dir, json_files[0])
            
        print(f"📖 Loading Report: {path}")
        with open(path, 'r') as f:
            return json.load(f)
            
    def generate_plan(self):
        candidates = self.report.get("refactoring_candidates", [])
        
        if not candidates:
            print("✅ No refactoring needed. System is optimal.")
            return self.plan
            
        for candidate in candidates:
            confidence = candidate.get("confidence", 0.0)
            
            if confidence < CONFIDENCE_THRESHOLD:
                status = "REVIEW_REQUIRED"
                reason = f"Low confidence ({confidence:.2f} < {CONFIDENCE_THRESHOLD})"
            else:
                status = "READY_TO_EXECUTE"
                reason = "Auto-approved by confidence check"
                
            # Construct Action
            target_file = candidate.get("target")
            # Config changes are generally safe, but critical for performance
            priority = "HIGH" if "threshold" in target_file or "config" in target_file else "MEDIUM"
                
            action = {
                "type": "UPDATE_CONFIG",
                "file": target_file,
                "key": candidate.get("key"),
                "new_value": candidate.get("suggested_value"),
                "priority": priority,
                "test_command": "python3 test_srie_core.py",
                "status": status,
                "meta": {
                    "reason": candidate.get("reason"),
                    "confidence": confidence
                }
            }
            self.plan["actions"].append(action)
            
        return self.plan
        
    def save_plan(self):
        plans_dir = os.path.join(self.base_dir, "plans")
        os.makedirs(plans_dir, exist_ok=True)
        
        plan_path = os.path.join(plans_dir, f"{self.plan['plan_id']}.json")
        
        with open(plan_path, 'w') as f:
            json.dump(self.plan, f, indent=2)
        print(f"📝 Plan saved to: {plan_path}")

if __name__ == "__main__":
    print("🧠 SRIE Planner v0.1 Starting...")
    try:
        planner = Planner()
        plan = planner.generate_plan()
        print(json.dumps(plan, indent=2))
        planner.save_plan()
    except Exception as e:
        print(f"❌ Error: {e}")
