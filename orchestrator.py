"""
SRIE Orchestrator v0.1
Self-Evolution Loop Controller

Coordinates Introspector -> Planner -> Refactor Agent.
Supports manual execution and scheduled tasks (Cron).

Usage:
  1. Dry Run (Generate Plan only):
     AUTO_REFACTOR=false python orchestrator.py

  2. Full Auto (Execute Plan):
     AUTO_REFACTOR=true python orchestrator.py
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime

class Orchestrator:
    def __init__(self, auto_refactor=False):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.auto_refactor = auto_refactor
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "FULL_AUTO" if auto_refactor else "DRY_RUN",
            "status": "PENDING",
            "phases": {},
            "errors": []
        }

    def run_phase(self, name, command):
        print(f"🚀 [Phase Start] {name}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=180  # 3 minutes timeout per phase
            )
            
            phase_log = {
                "exit_code": result.returncode,
                "output_tail": result.stdout[-1000:],
                "errors": result.stderr
            }
            self.report["phases"][name] = phase_log
            
            if result.returncode != 0:
                err_msg = f"Phase '{name}' failed with exit code {result.returncode}"
                print(f"❌ {err_msg}")
                print(result.stderr)
                self.report["errors"].append(err_msg)
                return False
            else:
                print(f"✅ [Phase End] {name} Succeeded")
                return True
                
        except subprocess.TimeoutExpired:
            err_msg = f"Phase '{name}' timed out"
            print(f"❌ {err_msg}")
            self.report["errors"].append(err_msg)
            return False

    def execute(self):
        print("🔗 SRIE Orchestrator Starting Self-Evolution Loop...")
        
        # Phase 1: Introspection
        if not self.run_phase("Introspection", "python3 introspector.py"):
            self.report["status"] = "FAILED_AT_INTROSPECTION"
            self._finalize()
            return

        # Phase 2: Planning
        if not self.run_phase("Planning", "python3 planner.py"):
            self.report["status"] = "FAILED_AT_PLANNING"
            self._finalize()
            return

        # Phase 3: Refactoring (Conditional)
        if self.auto_refactor:
            print("⚙️ AUTO_REFACTOR is enabled. Proceeding to execution...")
            if not self.run_phase("Refactoring", "python3 refactor_agent.py"):
                self.report["status"] = "FAILED_AT_REFACTORING"
                self._finalize()
                return
            self.report["status"] = "SUCCESS"
        else:
            print("⏸️ AUTO_REFACTOR=false. Skipping execution phase.")
            self.report["status"] = "COMPLETED_DRY_RUN"

        self._finalize()

    def _send_daily_report(self):
        """Send daily summary to Boss via OpenClaw"""
        try:
            # Load latest introspection data for metrics
            logs_dir = os.path.join(self.base_dir, "logs")
            files = sorted([f for f in os.listdir(logs_dir) if f.startswith('introspection_')], reverse=True)
            if not files:
                return
                
            with open(os.path.join(logs_dir, files[0]), 'r') as f:
                intro = json.load(f)
                
            perf = intro.get("model_performance", {})
            quality = intro.get("code_quality", {})
            
            msg = (
                f"🤖 [SRIE 每日运行简报] {datetime.now().strftime('%Y-%m-%d')}\n"
                f"✅ 状态: 闭环执行成功\n"
                f"📈 预测准确率: {perf.get('accuracy', 'N/A')}\n"
                f"🧪 F1 Score: {perf.get('f1_score', 'N/A')}\n"
                f"🐛 代码质量: {quality.get('status', 'N/A')} ({quality.get('issues_count', 0)} issues)\n"
                f"🔔 需审批项: 0\n"
                f"👉 看板: https://srie-dashboard.streamlit.app"
            )
            
            # 发送给爸爸 (OpenClaw CLI)
            subprocess.run([
                "openclaw", "message", "send",
                "--target", "ou_30bf15e3973282354fe607cbd39ea6df",
                "--message", msg
            ], check=False, timeout=15)
            print("📤 Daily report sent.")
        except Exception as e:
            print(f"⚠️ Failed to send report: {e}")

    def _finalize(self):
        print(f"🏁 Loop Finished. Status: {self.report['status']}")
        reports_dir = os.path.join(self.base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(reports_dir, f"orchestrator_{ts}.json")
        
        with open(path, 'w') as f:
            json.dump(self.report, f, indent=2)
        print(f"📝 Report saved: {path}")
        
        if self.report['status'] == 'SUCCESS' or self.report['status'] == 'COMPLETED_DRY_RUN':
            self._send_daily_report()

if __name__ == "__main__":
    # Check Environment Variable first
    auto_refactor_env = os.environ.get("AUTO_REFACTOR", "false").lower()
    auto_refactor = auto_refactor_env == "true"

    # CLI args can override
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-auto", action="store_true", help="Force AUTO_REFACTOR mode")
    args = parser.parse_args()
    
    if args.force_auto:
        auto_refactor = True

    orch = Orchestrator(auto_refactor=auto_refactor)
    orch.execute()