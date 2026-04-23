"""
教育领域适配器 (Cognitive Metabolism - CMD)
基于 VMN 核心引擎，检测学习过程中的认知过载与效率崩塌。
"""

from srie_core import SRIEEngine, VMNResult

class EducationAdvisor:
    def __init__(self):
        # 认知代谢阈值: 0.16 (即休息/学习 >= 0.16)
        self.engine = SRIEEngine(domain="cognitive")

    def analyze_study_cycle(self, study_hours: float, rest_hours: float) -> dict:
        """
        :param study_hours: 学习时长 (代表认知负荷积累) -> Dissipation
        :param rest_hours: 休息时长 (代表认知恢复) -> Perturbation
        """
        if study_hours <= 0:
            return {"status": "INFO", "msg": "没有学习压力？那当然不会崩溃。"}

        result: VMNResult = self.engine.analyze(
            perturbation=rest_hours, 
            dissipation=study_hours
        )

        # 业务层解读
        business_msg = ""
        if result.is_safe:
            business_msg = (
                f"✅ **节奏健康**。你的劳逸结合比例安全。\n"
                f"VMN ({result.current_vmn:.3f}) 在安全线以上。继续保持！"
            )
        else:
            business_msg = (
                f"🚨 **高危预警：认知过载！**\n"
                f"你正在逼近“填鸭式崩溃”的红线。大脑将在约 {result.time_to_collapse:.2f} 个时间单位后宕机。\n"
                f"💊 **处方**：为了救活你的学习效率，必须将休息时间从 {rest_hours:.2f}h 提升至 {result.required_perturbation:.2f}h。"
            )

        return {
            "vmn": result.current_vmn,
            "safe": result.is_safe,
            "collapse_time": result.time_to_collapse,
            "msg": business_msg
        }