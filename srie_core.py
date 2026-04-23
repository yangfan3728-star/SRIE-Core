"""
SRIE-Core: System Resilience & Intervention Engine
基于 VMN 统一动力学理论的预测与干预引擎

核心能力:
1. 计算活性维持数 (VMN = Perturbation / Dissipation)
2. 检测相变状态 (Criticality Check)
3. 预测崩溃时间 (Time-to-Collapse Prediction)
4. 生成最小干预处方 (Intervention Prescription)
"""

import math
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class VMNResult:
    """分析结果数据类"""
    current_vmn: float
    threshold_vmn: float
    is_safe: bool
    safety_margin: float  # (VMN - VMN_c) / VMN_c
    time_to_collapse: Optional[float]  # None 表示安全
    required_perturbation: float  # 为了达到安全所需的最小扰动值
    message: str

class SRIEEngine:
    """
    SRIE 核心预测引擎
    """
    
    # 📚 领域临界阈值库 (来源于 agi-srie 实验数据)
    # VMN = 扰动率 (Perturbation) / 耗散率 (Dissipation)
    DOMAIN_THRESHOLDS = {
        "cognitive": 0.160,      # 认知代谢 (CMD) - 学习/休息比
        "swarm": 0.096,          # 群体智慧 (Swarm Cocoon) - 多样性维持
        "trust": 0.040,          # 社交信任修复 - 谣言环境下的信任底线
        "interest": 0.008,       # 兴趣衰减 (Interest Decay) - 推荐算法防流失
        "custom": None           # 用户自定义
    }

    def __init__(self, domain: str = "cognitive", custom_threshold: float = None):
        if domain == "custom":
            if custom_threshold is None:
                raise ValueError("Custom domain requires a threshold value.")
            self.threshold_vmn = custom_threshold
        else:
            self.threshold_vmn = self.DOMAIN_THRESHOLDS.get(domain)
            if self.threshold_vmn is None:
                raise ValueError(f"Unknown domain: {domain}. Options: {list(self.DOMAIN_THRESHOLDS.keys())}")
        
        self.domain = domain

    def calculate_vmn(self, perturbation: float, dissipation: float) -> float:
        """计算当前系统的 VMN (活性维持数)"""
        if dissipation == 0:
            return float('inf') # 没有耗散，理论上永远安全
        return perturbation / dissipation

    def analyze(self, perturbation: float, dissipation: float, activity_level: float = 1.0, collapse_threshold: float = 0.05) -> VMNResult:
        """
        分析系统状态、预测崩溃时间并生成干预处方
        
        参数:
            perturbation (mu): 正向扰动率 (如休息频率、探索率)
            dissipation (lambda): 负向耗散率 (如学习压力、信息茧房引力)
            activity_level: 当前活性指标 (归一化为 1.0)
            collapse_threshold: 定义系统"死亡"的活性水平 (默认 0.05)
        """
        
        # 1. 计算当前 VMN
        current_vmn = self.calculate_vmn(perturbation, dissipation)
        is_safe = current_vmn >= self.threshold_vmn
        safety_margin = (current_vmn - self.threshold_vmn) / self.threshold_vmn if self.threshold_vmn > 0 else 0
        
        # 2. 预测崩溃时间 (Time-to-Collapse)
        # 模型假设：活性以指数形式衰减 A(t) = A_0 * exp((mu - lambda) * t)
        # 当 VMN < VMN_c 时，通常意味着 mu < lambda (或等效的净衰减)
        # 崩溃时间 t = ln(collapse_threshold / activity_level) / (mu - lambda)
        
        time_to_collapse = None
        if not is_safe:
            # 净衰减率
            net_decay = perturbation - dissipation # 通常为负数
            
            if net_decay < 0:
                # 计算衰减到 collapse_threshold 所需时间
                # t = ln(threshold/initial) / net_decay
                # 注意：net_decay 是负数，ln(small/large) 也是负数，结果为正
                if activity_level > collapse_threshold:
                    time_to_collapse = math.log(collapse_threshold / activity_level) / net_decay
            else:
                # 特殊情况：mu > lambda (系统增长) 但 mu/lambda < VMN_c
                # 这在某些非线性相变模型中可能出现（亚稳态），此时系统不会指数衰减但处于危险边缘
                # 为简化，标记为 None 或给一个长警告
                time_to_collapse = None 

        # 3. 计算干预处方
        # 目标: mu_new / lambda >= VMN_c  => mu_new >= lambda * VMN_c
        required_perturbation = self.threshold_vmn * dissipation
        
        # 4. 生成建议消息
        if is_safe:
            msg = f"✅ 系统处于健康状态。VMN ({current_vmn:.3f}) > 阈值 ({self.threshold_vmn:.3f})。安全裕度: {safety_margin:.1%}"
        else:
            needed_increase = required_perturbation - perturbation
            collapse_msg = ""
            if time_to_collapse is not None:
                collapse_msg = f"预计在 {time_to_collapse:.1f} 个单位时间内系统活性将跌破 {collapse_threshold:.0%}。\n"
            
            msg = (
                f"🚨 警告：系统处于危险区！VMN ({current_vmn:.3f}) < 阈值 ({self.threshold_vmn:.3f})。\n"
                f"{collapse_msg}"
                f"💊 处方：需将扰动率至少提升 {needed_increase:.3f} (从 {perturbation:.3f} 提至 {required_perturbation:.3f}) 以避免崩溃。"
            )

        return VMNResult(
            current_vmn=current_vmn,
            threshold_vmn=self.threshold_vmn,
            is_safe=is_safe,
            safety_margin=safety_margin,
            time_to_collapse=time_to_collapse,
            required_perturbation=required_perturbation,
            message=msg
        )