import re
from typing import Any, Dict, Iterable, List, Optional


def sanitize_material_name(name: Optional[str]) -> str:
    if not name:
        name = 'Material'
    name = re.sub(r'[.$&*~\'|\[\]{};"<>?/\\]', '_', name)
    name = name.replace(' ', '_')
    name = re.sub(r'_+', '_', name).strip('_')
    if len(name) > 80:
        name = name[:80].rstrip('_')
    return name or 'Material'


class AbaqusMaterialExporter:
    def __init__(self, material_data: Dict[str, Any]):
        self.material_data = material_data
        self.material_name = sanitize_material_name(
            material_data.get('MTNAME', {}).get('name', 'Deform_Material')
        )

    def generate(self) -> str:
        lines = [f'*Material, name={self.material_name}']
        self._append_density(lines)
        self._append_elastic(lines)
        self._append_scalar_or_curve(lines, 'THRCND', 'Conductivity')
        self._append_scalar_or_curve(lines, 'HEATCP', 'Specific Heat')
        self._append_expansion(lines)
        self._append_inelastic_heat_fraction(lines)
        self._append_plastic(lines)
        return '\n'.join(lines) + '\n'

    def save(self, output_path: str) -> str:
        content = self.generate()
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return output_path

    def _format(self, value: Any) -> str:
        if isinstance(value, float):
            return f'{value:g}'
        return str(value)

    def _append_block(self, lines: List[str], keyword: str, rows: Iterable[Iterable[Any]], options: Optional[Dict[str, Any]] = None):
        header = f'*{keyword}'
        if options:
            for key, value in options.items():
                header += f', {key}={value}'
        lines.append(header)
        for row in rows:
            lines.append(', '.join(self._format(item) for item in row))

    def _append_density(self, lines: List[str]):
        data = self.material_data.get('MASDEN')
        if data and data.get('value') is not None:
            self._append_block(lines, 'Density', [[data['value']]])

    def _append_elastic(self, lines: List[str]):
        young = self.material_data.get('YOUNG', {}).get('value')
        poisson = self.material_data.get('POISON', {}).get('value')
        if young is not None and poisson is not None:
            self._append_block(lines, 'Elastic', [[young, poisson]])

    def _append_scalar_or_curve(self, lines: List[str], source_key: str, abaqus_keyword: str):
        data = self.material_data.get(source_key)
        if not data:
            return
        curve_data = data.get('curve_data') or []
        if curve_data:
            rows = [[point.get('value'), point.get('temperature')] for point in curve_data]
            self._append_block(lines, abaqus_keyword, rows, {'dependencies': 1})
        elif data.get('value') is not None:
            self._append_block(lines, abaqus_keyword, [[data['value']]])

    def _append_expansion(self, lines: List[str]):
        data = self.material_data.get('EXPAND')
        if not data:
            return
        zero = data.get('reference_temp', 20.0)
        curve_data = data.get('curve_data') or []
        if curve_data:
            rows = [[point.get('coefficient'), point.get('temperature')] for point in curve_data]
        elif data.get('coefficient') is not None:
            rows = [[data['coefficient']]]
        else:
            return
        self._append_block(lines, 'Expansion', rows, {'zero': zero})

    def _append_inelastic_heat_fraction(self, lines: List[str]):
        data = self.material_data.get('FRAE2H')
        if data and data.get('value') is not None:
            lines.append('*Inelastic Heat Fraction')
            lines.append(f"{self._format(data['value'])},")

    def _append_plastic(self, lines: List[str]):
        fstres = self.material_data.get('FSTRES')
        if not fstres:
            return
        strain = fstres.get('strain_data') or []
        temperatures = fstres.get('temperature_data') or []
        rates = fstres.get('strain_rate_data') or [None]
        stress_data = fstres.get('stress_data') or []
        is_3d = bool(stress_data and isinstance(stress_data[0], list) and stress_data[0] and isinstance(stress_data[0][0], list))
        for temp_index, temperature in enumerate(temperatures):
            if temp_index >= len(stress_data):
                continue
            temp_block = stress_data[temp_index]
            if is_3d:
                for rate_index, rate in enumerate(rates):
                    if rate_index >= len(temp_block):
                        continue
                    rows = [[stress, eps, temperature] for eps, stress in zip(strain, temp_block[rate_index])]
                    options = {'rate': rate} if rate is not None else None
                    self._append_block(lines, 'Plastic', rows, options)
            else:
                rows = [[stress, eps, temperature] for eps, stress in zip(strain, temp_block)]
                self._append_block(lines, 'Plastic', rows)
