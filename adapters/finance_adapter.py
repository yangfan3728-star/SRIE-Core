"""
金融领域适配器 (Market Crash / Trust Recovery)
基于 VMN 核心引擎，预测市场信心崩塌与流动性危机。
映射逻辑：信任修复模型 (Trust Recovery Model)
"""

from srie_core import SRIEEngine, VMNResult

class FinanceAdvisor:
    def __init__(self):
        # 信任/市场模型，VMN_c = 0.04
        # 意味着：每 1 单位的恐慌流出，至少需要 0.04 单位的流动性注入才能维持系统存活
        self.engine = SRIEEngine(domain="trust")

    def analyze_market_sentiment(self, market_volatility: float, liquidity_injection: float, current_sentiment: float = 1.0) -> dict:
        """
        :param market_volatility: 市场波动率/恐慌指数 (Dissipation, lambda)
        :param liquidity_injection: 流动性注入/利好消息强度 (Perturbation, mu)
        :param current_sentiment: 当前市场信心指数 (0~1)
        """
        if market_volatility <= 0:
            return {"status": "INFO", "msg": "市场无恐慌情绪，非常健康。"}

        result: VMNResult = self.engine.analyze(
            perturbation=liquidity_injection, 
            dissipation=market_volatility,
            activity_level=current_sentiment
        )

        business_msg = ""
        if result.is_safe:
            business_msg = (
                f"✅ **市场情绪稳定**。流动性足以支撑当前抛压。\n"
                f"VMN ({result.current_vmn:.4f}) > 0.04 安全线。"
            )
        else:
            business_msg = (
                f"📉 **崩盘预警 (Crash Alert)**！\n"
                f"市场信心正在快速流失，流动性注入不足以对冲恐慌。\n"
                f"预计 {result.time_to_collapse:.2f} 小时后市场将进入“流动性枯竭”状态 (信心指数 < 5%)。\n"
                f"💊 **救市处方**: 必须立即增加 {result.required_perturbation:.4f} 的流动性注入 (或平准基金入市)。"
            )

        return {
            "vmn": result.current_vmn,
            "safe": result.is_safe,
            "crash_time": result.time_to_collapse,
            "msg": business_msg
        }