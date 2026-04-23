"""
SRIE-Core: System Resilience & Intervention Engine
基于 VMN 统一动力学理论的预测与干预引擎

核心功能：
1. 预测系统崩溃时间 (Time-to-Collapse Prediction)
2. 生成最小干预处方 (Minimal Intervention Prescription)
"""

class SRIEEngine:
    def __init__(self):
        # 统一动力学阈值库 (来源于 agi-srie 实验数据)
        # Key: 动力学类型, Value: 临界 VMN 值 (Vc)
        self.thresholds = {
            "trust_recovery": 0.040,   # 社交信任修复 (共识类)
            "cognitive_metabolism": 0.160, # 认知代谢 CMD (主动恢复类)
            "swarm_diversity": 0.096,  # 群体智慧/反茧房 (共识类, alpha=0.5)
            "interest_retention": 0.008, # 兴趣留存 (算法类)
            "ecology_allee": 0.002     # 生态 Allee 效应 (第三类)
        }

    def get_vmn(self, perturbation: float, dissipation: float) -> float:
        """计算当前系统的 VMN (活性维持数)"""
        if dissipation == 0:
            return float('inf')
        return perturbation / dissipation

    def predict_status(self, model_type: str, perturbation: float, dissipation: float):
        """
        预测系统状态
        :param model_type: 动力学类型 (如 'trust_recovery')
        :param perturbation: 正向扰动强度 (mu)
        :param dissipation: 负向耗散强度 (lambda)
        :return: dict 包含 vmn, status, margin
        """
        if model_type not in self.thresholds:
            raise ValueError(f"未知模型类型: {model_type}")

        vmn = self.get_vmn(perturbation, dissipation)
        vc = self.thresholds[model_type]
        margin = vmn - vc
        
        if margin > 0:
            status = "HEALTHY (Super-critical)"
        elif margin > -0.01:
            status = "WARNING (Near-critical)"
        else:
            status = "CRITICAL (Sub-critical)"

        return {
            "model": model_type,
            "vmn": vmn,
            "critical_value": vc,
            "margin": margin,
            "status": status
        }

    def recommend_intervention(self, model_type: str, current_perturbation: float, current_dissipation: float):
        """
        生成最小干预处方
        计算为了让 VMN >= Vc，需要增加多少扰动 (delta_mu) 或 减少多少耗散 (delta_lambda)
        """
        result = self.predict_status(model_type, current_perturbation, current_dissipation)
        
        if result["status"].startswith("HEALTHY"):
            return {"action": "MAINTAIN", "message": "系统处于健康状态，无需干预。"}

        vc = result["critical_value"]
        
        # 方案 A: 增加扰动 (Mu Increase)
        # Target: (mu + delta) / lambda >= vc
        # delta >= vc * lambda - mu
        required_perturbation = vc * current_dissipation
        delta_mu = required_perturbation - current_perturbation
        
        # 方案 B: 减少耗散 (Lambda Decrease)
        # Target: mu / (lambda - delta) >= vc
        # lambda - delta <= mu / vc
        # delta >= lambda - (mu / vc)
        required_dissipation = current_perturbation / vc
        delta_lambda = current_dissipation - required_dissipation
        
        return {
            "action": "INTERVENE",
            "current_vmn": result["vmn"],
            "target_vmn": vc,
            "plan_a_increase_perturbation": f"需将扰动率从 {current_perturbation} 提升至 {required_perturbation:.4f} (+{delta_mu:.4f})",
            "plan_b_reduce_dissipation": f"需将耗散率从 {current_dissipation} 降低至 {required_dissipation:.4f} (-{delta_lambda:.4f})"
        }
