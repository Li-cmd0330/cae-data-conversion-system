from bisect import bisect_left
from typing import Iterable, List, Sequence


def linear_interpolate(x: Sequence[float], y: Sequence[float], target_x: float) -> float:
    if len(x) != len(y) or not x:
        raise ValueError('x 和 y 长度必须一致且不能为空')
    if len(x) == 1:
        return float(y[0])
    if target_x <= x[0]:
        return float(y[0])
    if target_x >= x[-1]:
        return float(y[-1])
    index = bisect_left(x, target_x)
    x0, x1 = x[index - 1], x[index]
    y0, y1 = y[index - 1], y[index]
    if x1 == x0:
        return float(y0)
    return float(y0 + (y1 - y0) * (target_x - x0) / (x1 - x0))


def nearest_interpolate(x: Sequence[float], y: Sequence[float], target_x: float) -> float:
    if len(x) != len(y) or not x:
        raise ValueError('x 和 y 长度必须一致且不能为空')
    index = min(range(len(x)), key=lambda i: abs(x[i] - target_x))
    return float(y[index])


class FlowStressInterpolator:
    def __init__(self, fstres_data):
        self.strain = fstres_data.get('strain_data') or []
        self.temperature = fstres_data.get('temperature_data') or []
        self.strain_rate = fstres_data.get('strain_rate_data') or []
        self.stress = fstres_data.get('stress_data') or []

    def predict(self, strain: float, strain_rate: float = None, temperature: float = None, method: str = 'linear') -> float:
        if not self.stress:
            raise ValueError('缺少流动应力数据')
        temp_index = self._nearest_index(self.temperature, temperature) if temperature is not None and self.temperature else 0
        temp_block = self.stress[temp_index]
        is_3d = bool(temp_block and isinstance(temp_block[0], list))
        if is_3d:
            rate_index = self._nearest_index(self.strain_rate, strain_rate) if strain_rate is not None and self.strain_rate else 0
            curve = temp_block[rate_index]
        else:
            curve = temp_block
        if method == 'nearest':
            return nearest_interpolate(self.strain, curve, strain)
        return linear_interpolate(self.strain, curve, strain)

    def _nearest_index(self, values: Sequence[float], target: float) -> int:
        return min(range(len(values)), key=lambda i: abs(values[i] - target))
