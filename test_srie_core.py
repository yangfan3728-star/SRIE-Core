"""
SRIE-Core v0.1 测试与演示脚本
验证核心引擎和三个领域适配器的功能。
"""

import sys
import os

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from srie_core import SRIEEngine
from adapters.education_adapter import EducationAdvisor
from adapters.finance_adapter import FinanceAdvisor
from adapters.recommendation_adapter import RecommendationAdvisor

def run_tests():
    print("="*60)
    print("🚀 SRIE-Core v0.1 Test & Demo Suite")
    print("="*60)

    # 1. 核心引擎测试 (通用)
    print("\n📦 [1] 核心引擎通用测试 (Generic Core)")
    engine = SRIEEngine(domain="custom", custom_threshold=0.10)
    res = engine.analyze(perturbation=0.05, dissipation=1.0)
    print(f"   Custom VMN: {res.current_vmn:.3f} (Thresh: {res.threshold_vmn})")
    print(f"   Status: {'SAFE' if res.is_safe else 'CRITICAL'}")
    print(f"   Msg: {res.message[:60]}...")

    # 2. 教育模块测试 (CMD)
    print("\n🎓 [2] 教育模块测试 (Education - CMD)")
    edu = EducationAdvisor()
    
    # 场景 A: 健康学习
    print("   场景 A: 学 5h 休 1h (R=5)")
    r1 = edu.analyze_study_cycle(study_hours=5, rest_hours=1)
    print(f"   -> {r1['msg'][:50]}...")
    
    # 场景 B: 填鸭式学习 (危险)
    print("   场景 B: 学 10h 休 0.5h (R=20, 极度危险)")
    r2 = edu.analyze_study_cycle(study_hours=10, rest_hours=0.5)
    print(f"   -> {r2['msg'][:50]}...")

    # 3. 金融模块测试 (Market Crash)
    print("\n📈 [3] 金融模块测试 (Finance - Crash)")
    fin = FinanceAdvisor()
    
    # 场景 A: 市场稳定
    print("   场景 A: 波动 1.0, 注入 0.1")
    f1 = fin.analyze_market_sentiment(market_volatility=1.0, liquidity_injection=0.1)
    print(f"   -> {f1['msg'][:50]}...")

    # 场景 B: 崩盘边缘
    print("   场景 B: 波动 5.0, 注入 0.05 (注入不足)")
    f2 = fin.analyze_market_sentiment(market_volatility=5.0, liquidity_injection=0.05)
    print(f"   -> {f2['msg'][:50]}...")

    # 4. 推荐算法测试 (Churn)
    print("\n📱 [4] 推荐算法测试 (Recommendation - Churn)")
    rec = RecommendationAdvisor()

    # 场景 A: 健康
    print("   场景 A: 茧房力 1.0, 探索率 0.02 (2%)")
    c1 = rec.analyze_retention_risk(exploration_rate=0.02, homogeneity_force=1.0)
    print(f"   -> {c1['msg'][:50]}...")

    # 场景 B: 茧房危机
    print("   场景 B: 茧房力 2.0, 探索率 0.005 (0.5%)")
    c2 = rec.analyze_retention_risk(exploration_rate=0.005, homogeneity_force=2.0)
    print(f"   -> {c2['msg'][:50]}...")

    print("\n" + "="*60)
    print("✅ All Tests Completed.")
    print("="*60)

if __name__ == "__main__":
    run_tests()