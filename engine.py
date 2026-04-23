"""
SRIE-Core Engine v0.1
Vitality Maintenance Number (VMN) 预测与干预系统

核心理论: 
VMN = 正向扰动 (Perturbation) / 负向耗散 (Dissipation)
当 VMN < VMN_c (临界值) 时，系统将走向不可逆的软崩塌 (Soft Collapse)。
"""

import math
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class VMNResult:
    current_vmn: float
    threshold_vmn: float
    is_safe: bool
    safety_margin: float  # (VMN - VMN_c) / VMN_c
    time_to_collapse_days: Optional[float]  # None 表示安全
    required_perturbation: float  # 为了达到安全所需的最小扰动值
    intervention_message: str

class SRIEEngine:
    """
    SRIE 核心预测引擎
    """
    
    # 内置的各领域临界阈值 (来源于统一动力学论文的仿真结论)
    DOMAIN_THRESHOLDS = {
        "social_trust": 0.040,      # 信任修复 (Trust Discounting)
        "cognitive_metabolism": 0.160, # 认知代谢 (CMD)
        "swarm_cocoon": 0.096,      # 群体多样性 (Swarm Cocoon)
        "interest_decay": 0.008,    # 兴趣衰减 (Interest Discounting)
        "custom": None              # 用户自定义
    }

    def __init__(self, domain: str = "social_trust", custom_threshold: float = None):
        if domain == "custom":
            if custom_threshold is None:
                raise ValueError("Custom domain requires a threshold value.")
            self.threshold_vmn = custom_threshold
        else:
            self.threshold_vmn = self.DOMAIN_THRESHOLDS.get(domain)
            if self.threshold_vmn is None:
                raise ValueError(f"Unknown domain: {domain}")
        
        self.domain = domain

    def analyze(self, dissipation_rate: float, perturbation_rate: float, activity_level: float = 1.0, collapse_level: float = 0.05) -> VMNResult:
        """
        分析系统状态并预测崩溃时间
        
        参数:
            dissipation_rate (lambda): 系统固有耗散率 (如：每天流失 10% 用户 -> 0.1)
            perturbation_rate (mu): 系统当前正向扰动率 (如：每天带来 2% 新流量 -> 0.02)
            activity_level: 当前活性指标 (归一化为 1.0)
            collapse_level: 定义系统"死亡"的活性水平 (默认 0.05)
        """
        
        # 1. 计算当前 VMN
        if dissipation_rate == 0:
            current_vmn = float('inf') # 没有耗散，永远安全
        else:
            current_vmn = perturbation_rate / dissipation_rate
            
        is_safe = current_vmn >= self.threshold_vmn
        safety_margin = (current_vmn - self.threshold_vmn) / self.threshold_vmn
        
        # 2. 计算崩溃倒计时 (基于指数衰减模型)
        # 模型: A(t) = A_0 * exp((mu - lambda) * t)
        # 崩溃条件: A(t) <= collapse_level * A_0
        # 求解 t: exp((mu - lambda) * t) <= collapse_level
        #        (mu - lambda) * t <= ln(collapse_level)
        #        t >= ln(collapse_level) / (mu - lambda)
        # 注意: 只有当 mu < lambda 时 (VMN < 1)，才会崩溃。
        # 但根据 VMN 理论，当 mu/lambda < VMN_c 时，即便 mu 接近 lambda，系统也可能因为相变而死。
        # 这里我们简化为：如果 mu < lambda，则指数衰减。
        
        time_to_collapse = None
        
        if not is_safe:
            # 净衰减率 (Net Decay Rate)
            # 如果 mu > lambda (即 VMN > 1)，系统是增长的，理论上不会自然死 (除非有上限限制)
            # 如果 mu <= lambda，系统是衰减的
            
            if perturbation_rate < dissipation_rate:
                net_decay = dissipation_rate - perturbation_rate
                # 计算时间 (天/单位时间)
                # 取绝对值，因为 ln(0.05) 是负数
                time_to_collapse = abs(math.log(collapse_level)) / net_decay
            else:
                # 特殊相变情况: mu >= lambda 但 mu/lambda < VMN_c
                # 在论文中，这种情况通常意味着系统处于亚稳态，最终会因噪声崩溃
                # 此处简化：如果接近阈值，给出较长警告时间
                # 这里暂设为一个基于差距的经验值
                gap = self.threshold_vmn - current_vmn
                time_to_collapse = (1.0 / gap) * 10.0 # 经验公式：差距越小死得越慢
                
        # 3. 计算干预处方
        # 目标: mu_new / lambda >= threshold_vmn
        # mu_new >= threshold_vmn * lambda
        required_perturbation = self.threshold_vmn * dissipation_rate
        
        # 4. 生成建议消息
        if is_safe:
            msg = f"✅ 系统安全。当前 VMN ({current_vmn:.3f}) 高于临界值 ({self.threshold_vmn:.3f})。安全裕度: {safety_margin:.1%}"
        else:
            needed_increase = required_perturbation - perturbation_rate
            msg = (f"🚨 警告：系统处于危险区！当前 VMN ({current_vmn:.3f}) 低于临界值。"
                   f"必须在 {time_to_collapse:.1f} 个单位时间内采取行动！"
                   f"处方：将扰动率至少提升 {needed_increase:.3f} (从 {perturbation_rate:.3f} 提至 {required_perturbation:.3f})。")

        return VMNResult(
            current_vmn=current_vmn,
            threshold_vmn=self.threshold_vmn,
            is_safe=is_safe,
            safety_margin=safety_margin,
            time_to_collapse_days=time_to_collapse,
            required_perturbation=required_perturbation,
            intervention_message=msg
        )