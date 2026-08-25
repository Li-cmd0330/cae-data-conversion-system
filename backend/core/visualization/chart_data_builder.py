from typing import Any, Dict, List


class ChartDataBuilder:
    def build_flow_stress_chart(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        fstres = material_data.get('FSTRES') or {}
        strain = fstres.get('strain_data') or []
        temperatures = fstres.get('temperature_data') or []
        rates = fstres.get('strain_rate_data') or []
        stress_data = fstres.get('stress_data') or []
        series: List[Dict[str, Any]] = []

        is_3d = bool(stress_data and isinstance(stress_data[0], list) and stress_data[0] and isinstance(stress_data[0][0], list))
        if is_3d:
            for temp_index, temperature in enumerate(temperatures):
                if temp_index >= len(stress_data):
                    continue
                for rate_index, rate in enumerate(rates or [1]):
                    if rate_index >= len(stress_data[temp_index]):
                        continue
                    series.append({
                        'name': f'T={temperature:g}°C, ε̇={rate:g}/s',
                        'data': stress_data[temp_index][rate_index],
                    })
        else:
            for temperature, stress_row in zip(temperatures, stress_data):
                series.append({'name': f'{temperature:g}°C', 'data': stress_row})

        return {
            'x_axis': strain,
            'series': series,
            'meta': {
                'x_name': '应变',
                'y_name': '应力 MPa',
                'temperature_count': len(temperatures),
                'strain_rate_count': len(rates),
            }
        }

    def build_completeness_radar(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        groups = {
            '基本信息': ['MTNAME', 'UNIT'],
            '力学性能': ['YOUNG', 'POISON', 'FRAE2H', 'FPERV', 'FSTRES'],
            '热学性能': ['THRCND', 'HEATCP', 'MASDEN', 'EMSVTY', 'EXPAND'],
            '损伤模型': ['FRCMOD', 'HDNPHA'],
        }
        indicators = []
        values = []
        for name, fields in groups.items():
            score = round(sum(1 for field in fields if field in material_data) / len(fields) * 100, 2)
            indicators.append({'name': name, 'max': 100})
            values.append(score)
        return {'indicators': indicators, 'series': [{'name': '完整度', 'value': values}]}
