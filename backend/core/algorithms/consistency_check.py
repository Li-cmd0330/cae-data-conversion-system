from typing import Any, Dict, List


def check_monotonic(values: List[float], strict: bool = True) -> bool:
    if strict:
        return all(values[index] < values[index + 1] for index in range(len(values) - 1))
    return all(values[index] <= values[index + 1] for index in range(len(values) - 1))


def consistency_summary(material_data: Dict[str, Any]) -> Dict[str, Any]:
    issues = []
    fstres = material_data.get('FSTRES')
    if fstres:
        strain = fstres.get('strain_data') or []
        temp = fstres.get('temperature_data') or []
        if strain and not check_monotonic(strain):
            issues.append({'level': 'warning', 'field': 'FSTRES.strain_data', 'message': '应变数据非严格递增'})
        if temp and not check_monotonic(temp):
            issues.append({'level': 'warning', 'field': 'FSTRES.temperature_data', 'message': '温度数据非严格递增'})
    return {'passed': not any(item['level'] == 'error' for item in issues), 'issues': issues}
