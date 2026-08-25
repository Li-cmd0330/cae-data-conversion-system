import math
from typing import Sequence

import numpy as np


def johnson_cook(strain, strain_rate, temperature, A, B, n, C, m, ref_rate=1.0, ref_temp=20.0, melt_temp=600.0):
    thermal = max(0.0, min(1.0, (temperature - ref_temp) / (melt_temp - ref_temp)))
    rate_term = 1 + C * math.log(max(strain_rate, 1e-12) / ref_rate)
    return (A + B * (strain ** n)) * rate_term * (1 - thermal ** m)


def fit_johnson_cook_placeholder(strain: Sequence[float], stress: Sequence[float]):
    if not strain or not stress or len(strain) != len(stress):
        raise ValueError('strain 和 stress 长度必须一致且不能为空')
    strain_array = np.asarray(strain, dtype=float)
    stress_array = np.asarray(stress, dtype=float)
    A = float(stress_array[0])
    B = float(max(stress_array) - A)
    n = 0.2
    return {'A': A, 'B': B, 'n': n, 'C': 0.01, 'm': 1.0, 'note': '基础估算结果，可接入 scipy.optimize.curve_fit 做精确拟合'}
