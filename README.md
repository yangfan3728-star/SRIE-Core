# SRIE-Core (System Resilience & Intervention Engine)
> **基于 VMN 统一动力学理论的通用预测与干预引擎**
> 
> 核心能力：
> 1. **预测 (Prediction)**：基于耗散与扰动，计算系统“崩溃倒计时”。
> 2. **处方 (Prescription)**：生成维持系统存活的“最小干预参数”。

## 📦 目录结构
- `srie_core.py`: 核心引擎 (VMN Calculator, Collapse Predictor)
- `adapters/`: 领域适配器
  - `education.py`: 认知代谢 (CMD) 适配器
  - `finance.py`: 市场崩盘 (Market Crash) 适配器
  - `recommendation.py`: 推荐算法 (Interest Decay) 适配器

## 🚀 快速开始
```python
from srie_core import SRIEEngine

# 初始化引擎 (默认使用认知代谢模型)
engine = SRIEEngine(domain="cognitive")

# 诊断：假设学习 5 小时，休息 0.5 小时 (R=10, 极高压力)
# 耗散 (学习压力) = 1.0, 扰动 (休息) = 0.1
result = engine.diagnose(perturbation=0.1, dissipation=1.0)

print(result["message"])
# 🚨 警告：系统处于危险区！预计在 4.6 个单位时间内崩塌。
# 💊 处方：需增加休息率至 0.16。
```

---
*Powered by VMN Unified Dynamics Theory*