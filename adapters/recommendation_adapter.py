"""
推荐算法适配器 (Interest Decay / Filter Bubble)
基于 VMN 核心引擎，预测用户兴趣枯竭与信息茧房崩塌。
映射逻辑：兴趣衰减模型 (Interest Decay Model)
"""

from srie_core import SRIEEngine, VMNResult

class RecommendationAdvisor:
    def __init__(self):
        # 兴趣衰减模型，VMN_c = 0.008
        # 意味着：算法只需 0.8% 的随机探索率，即可对抗信息茧房的引力
        self.engine = SRIEEngine(domain="interest")

    def analyze_retention_risk(self, exploration_rate: float, homogeneity_force: float, current_user_engagement: float = 1.0) -> dict:
        """
        :param exploration_rate: 推荐系统的随机探索率 (Perturbation, mu)
        :param homogeneity_force: 算法同质化程度/信息茧房引力 (Dissipation, lambda)
        :param current_user_engagement: 当前用户活跃度/留存 (0~1)
        """
        if homogeneity_force <= 0:
            return {"status": "INFO", "msg": "无信息茧房效应，非常健康。"}

        result: VMNResult = self.engine.analyze(
            perturbation=exploration_rate, 
            dissipation=homogeneity_force,
            activity_level=current_user_engagement
        )

        business_msg = ""
        if result.is_safe:
            business_msg = (
                f"✅ **用户留存健康**。当前探索率足以打破茧房。\n"
                f"VMN ({result.current_vmn:.5f}) > 0.008 安全线。"
            )
        else:
            business_msg = (
                f"📱 **流失预警 (Churn Alert)**！\n"
                f"用户正在陷入信息茧房，兴趣正在快速枯竭。\n"
                f"预计 {result.time_to_collapse:.2f} 小时后用户活跃度将跌破 5%（流失）。\n"
                f"💊 **算法处方**: 必须立即将随机探索率 (epsilon) 从 {exploration_rate:.5f} 提升至 {result.required_perturbation:.5f} (约 {result.required_perturbation*100:.2f}%)。"
            )

        return {
            "vmn": result.current_vmn,
            "safe": result.is_safe,
            "churn_time": result.time_to_collapse,
            "msg": business_msg
        }