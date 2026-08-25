CONVERSION_FACTORS = {
    'stress': {
        ('MPa', 'Pa'): 1_000_000,
        ('Pa', 'MPa'): 1 / 1_000_000,
        ('MPa', 'GPa'): 0.001,
        ('GPa', 'MPa'): 1000,
    },
    'density': {
        ('kg/mm3', 'kg/m3'): 1_000_000_000,
        ('kg/m3', 'kg/mm3'): 1 / 1_000_000_000,
        ('g/cm3', 'kg/m3'): 1000,
        ('kg/m3', 'g/cm3'): 0.001,
    },
    'temperature': {},
}


def convert_unit(value: float, from_unit: str, to_unit: str, quantity: str) -> float:
    if from_unit == to_unit:
        return float(value)
    if quantity == 'temperature':
        return convert_temperature(value, from_unit, to_unit)
    factor = CONVERSION_FACTORS.get(quantity, {}).get((from_unit, to_unit))
    if factor is None:
        raise ValueError(f'不支持的单位换算: {quantity} {from_unit} -> {to_unit}')
    return float(value) * factor


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit == to_unit:
        return float(value)
    if from_unit == 'C' and to_unit == 'K':
        return float(value) + 273.15
    if from_unit == 'K' and to_unit == 'C':
        return float(value) - 273.15
    raise ValueError(f'不支持的温度换算: {from_unit} -> {to_unit}')
