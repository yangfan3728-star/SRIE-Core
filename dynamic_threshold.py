"""
SRIE Dynamic Thresholding Algorithm
自适应阈值计算模块

原理：
根据系统的“耗散波动率 (CV)"动态调整 VMN 安全阈值。
- 环境稳定时：保持基准阈值，避免过度敏感（假阳性）。
- 环境剧烈波动时（高 CV）：自动调高阈值，要求系统有更多的扰动（干预）才能视为安全。

公式：
V_threshold = V_base * (1 + alpha * max(0, CV - CV_baseline))
"""

import numpy as np
import sys
import os

class DynamicThreshold:
    def __init__(self, base_threshold=0.04, alpha=0.5, cv_baseline=0.2):
        """
        :param base_threshold: 基础阈值 (Static baseline)
        :param alpha: 敏感度系数 (波动每增加 1，阈值增加多少)
        :param cv_baseline: 基准波动率 (低于此值不进行调整)
        """
        self.base_threshold = base_threshold
        self.alpha = alpha
        self.cv_baseline = cv_baseline

    def calculate_cv(self, data_series):
        """计算变异系数 (Coefficient of Variation) = std / mean"""
        arr = np.array(data_series)
        if len(arr) < 2:
            return 0.0
        mean = np.mean(arr)
        if mean == 0:
            return 1.0 # Avoid division by zero
        std = np.std(arr)
        return std / mean

    def get_threshold(self, recent_dissipation_data):
        """
        根据近期的耗散数据计算当前应有的阈值
        :param recent_dissipation_data: List of recent dissipation values (e.g., volatility)
        """
        cv = self.calculate_cv(recent_dissipation_data)
        
        # 仅当波动率超过基准线时才增加阈值
        adjustment = max(0, cv - self.cv_baseline)
        dynamic_val = self.base_threshold * (1 + self.alpha * adjustment)
        
        return {
            "current_cv": round(cv, 4),
            "base_threshold": self.base_threshold,
            "dynamic_threshold": round(dynamic_val, 4),
            "adjustment_factor": round(1 + self.alpha * adjustment, 2)
        }

if __name__ == "__main__":
    # 测试示例
    dt = DynamicThreshold()
    
    # 场景 1: 稳定市场 (低波动)
    stable = [2.0, 2.1, 1.9, 2.0, 2.05]
    print(f"Stable Market: {dt.get_threshold(stable)}")
    
    # 场景 2: 恐慌市场 (高波动)
    panic = [2.0, 5.0, 1.0, 6.0, 2.0]
    print(f"Panic Market: {dt.get_threshold(panic)}")
