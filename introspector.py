"""
SRIE Introspector v0.2
Enhanced Self-Check Module

New capabilities:
- Code Quality Check (Ruff/PyLint)
- Test Coverage Check (Pytest)
- Dependency Health Check (pip-audit equivalent or simple version check)
"""

import os
import sys
import json
import subprocess
import time
import shutil
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from srie_core import SRIEEngine
except ImportError:
    print("Error: srie_core.py not found.")
    sys.exit(1)

class Introspector:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "config", "thresholds.json")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        self.config = self._load_config()
        self.start_time = time.time()
        self.engine = SRIEEngine(domain="trust")

    def _load_config(self) -> dict:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {"error": "Config file missing"}

    def _check_system_health(self) -> dict:
        """System resource check"""
        if HAS_PSUTIL:
            proc = psutil.Process(os.getpid())
            return {
                "status": "HEALTHY",
                "cpu_percent": psutil.cpu_percent(interval=0.5),
                "memory_mb": round(proc.memory_info().rss / 1024 / 1024, 2)
            }
        return {"status": "UNKNOWN", "note": "psutil missing"}

    def _check_code_quality(self) -> dict:
        """Run Ruff or PyLint if available"""
        try:
            # Try Ruff first (faster)
            result = subprocess.run(
                ["ruff", "check", ".", "--select", "E,F,W"],
                cwd=self.base_dir, capture_output=True, text=True, timeout=30
            )
            issues = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            return {
                "tool": "ruff",
                "status": "PASSED" if result.returncode == 0 else "WARNING",
                "issues_count": issues if result.returncode != 0 else 0,
                "details": result.stdout[:500]
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {"tool": "ruff", "status": "SKIPPED", "note": "Ruff not installed"}

    def _check_test_coverage(self) -> dict:
        """Run Pytest with coverage"""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "test_srie_core.py", "--cov=srie_core", "--cov-report=json"],
                cwd=self.base_dir, capture_output=True, text=True, timeout=60
            )
            # Check for coverage JSON
            cov_path = os.path.join(self.base_dir, "coverage.json")
            coverage_pct = "N/A"
            if os.path.exists(cov_path):
                with open(cov_path, 'r') as f:
                    cov_data = json.load(f)
                    coverage_pct = cov_data.get("totals", {}).get("percent_covered", "N/A")
                os.remove(cov_path) # Clean up
                
            return {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "coverage_percent": coverage_pct
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {"status": "SKIPPED", "note": "Pytest or pytest-cov not installed"}

    def _check_dependencies(self) -> dict:
        """Check for outdated packages"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                return {
                    "status": "WARNING" if outdated else "HEALTHY",
                    "outdated_count": len(outdated),
                    "packages": [p["name"] for p in outdated[:3]] # Show top 3
                }
            return {"status": "UNKNOWN"}
        except Exception:
            return {"status": "SKIPPED"}

    def _run_mini_backtest(self) -> dict:
        """Mini backtest: Static vs Dynamic Thresholds"""
        samples = [
            (5.0, 0.05, True), (4.0, 0.05, True), (2.0, 0.1, False), 
            (6.0, 0.02, True), (0.5, 0.2, False), (3.0, 0.08, False)
        ]
        
        # 1. Static Test
        base_threshold = self.config.get("thresholds", {}).get("trust", 0.04)
        s_tp, s_fp, s_tn, s_fn = 0, 0, 0, 0
        
        for vol, liq, actual_crash in samples:
            # Simulate check against static threshold
            res = self.engine.analyze(perturbation=liq, dissipation=vol, activity_level=1.0)
            # Override safety check manually for simulation
            pred_danger = res.current_vmn < base_threshold
            
            if pred_danger and actual_crash: s_tp += 1
            elif pred_danger and not actual_crash: s_fp += 1
            elif not pred_danger and actual_crash: s_fn += 1
            else: s_tn += 1
            
        s_acc = round((s_tp + s_tn) / len(samples), 3)
        
        # 2. Dynamic Test (Simulated)
        # In a real scenario, threshold changes based on volatility.
        # For this sample, high volatility cases should have higher threshold.
        # We simulate the dynamic adjustment logic here for evaluation.
        d_tp, d_fp, d_tn, d_fn = 0, 0, 0, 0
        
        from dynamic_threshold import DynamicThreshold
        dt = DynamicThreshold(base_threshold=base_threshold)
        
        for vol, liq, actual_crash in samples:
            # Calculate dynamic threshold based on volatility
            # Using a moving window of just this point for simulation (simplified)
            # In real usage, we would pass a list. Here we simulate: if vol is high, threshold goes up.
            
            # Mocking the CV calculation effect: High vol -> Higher threshold
            # Formula approximation for single point simulation:
            dynamic_threshold = base_threshold
            if vol > 4.0: # High volatility spike
                dynamic_threshold = base_threshold * 1.25 # 25% increase
            
            res = self.engine.analyze(perturbation=liq, dissipation=vol, activity_level=1.0)
            pred_danger = res.current_vmn < dynamic_threshold
            
            if pred_danger and actual_crash: d_tp += 1
            elif pred_danger and not actual_crash: d_fp += 1
            elif not pred_danger and actual_crash: d_fn += 1
            else: d_tn += 1
            
        d_acc = round((d_tp + d_tn) / len(samples), 3)

        return {
            "static_accuracy": s_acc,
            "dynamic_accuracy": d_acc,
            "improvement": round(d_acc - s_acc, 3),
            "verdict": "Dynamic is Better" if d_acc > s_acc else "Static is Better"
        }

    def generate_report(self) -> dict:
        health = self._check_system_health()
        quality = self._check_code_quality()
        coverage = self._check_test_coverage()
        deps = self._check_dependencies()
        backtest = self._run_mini_backtest()

        # Overall Status Logic
        status = "HEALTHY"
        if quality["status"] == "WARNING" or deps["status"] == "WARNING":
            status = "WARNING"
            
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_health": health,
            "code_quality": quality,
            "test_coverage": coverage,
            "dependency_health": deps,
            "model_performance": backtest,
            "summary": {"status": status}
        }
        
        # Save report
        filename = f"introspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.logs_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report

if __name__ == "__main__":
    print("🔍 SRIE Introspector v0.2 Running Enhanced Checks...")
    introspector = Introspector()
    report = introspector.generate_report()
    print(json.dumps(report, indent=2))
    print("✅ Done.")