import csv
import json
from datetime import datetime
from typing import Any, Dict, List


class MultiFormatExporter:
    def export_to_json(self, material_data: Dict[str, Any], output_path: str) -> bool:
        try:
            export_data = {
                'metadata': {
                    'export_time': datetime.now().isoformat(),
                    'format_version': '2.0',
                    'tool': 'CAE Data Converter Web',
                },
                'material_data': material_data,
            }
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(export_data, file, indent=2, ensure_ascii=False)
            return True
        except Exception as exc:
            print(f'导出JSON失败: {exc}')
            return False

    def export_to_csv(self, material_data: Dict[str, Any], output_path: str) -> bool:
        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(['CAE材料属性数据表'])
                writer.writerow(['导出时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                writer.writerow(['一、基本信息'])
                if 'MTNAME' in material_data:
                    mtname = material_data['MTNAME']
                    writer.writerow(['材料名称', mtname.get('name', ''), 'Material Name'])
                    writer.writerow(['材料编号', mtname.get('id', ''), 'Material ID'])
                if 'UNIT' in material_data:
                    writer.writerow(['单位系统', material_data['UNIT'], 'Unit System'])

                self._write_property_group(writer, '二、力学性能', material_data, {
                    'YOUNG': ('杨氏模量 (MPa)', "Young's Modulus"),
                    'POISON': ('泊松比', "Poisson's Ratio"),
                    'FRAE2H': ('塑性功转热系数', 'Inelastic Heat Fraction'),
                    'FPERV': ('摩擦系数', 'Friction Coefficient'),
                })
                self._write_property_group(writer, '三、热学性能', material_data, {
                    'THRCND': ('热传导系数 (W/m·K)', 'Thermal Conductivity'),
                    'HEATCP': ('比热容 (J/kg·K)', 'Specific Heat'),
                    'EMSVTY': ('发射率', 'Emissivity'),
                    'MASDEN': ('密度 (kg/mm³)', 'Density'),
                })

                if 'EXPAND' in material_data:
                    expand = material_data['EXPAND']
                    writer.writerow(['热膨胀系数 (1/°C)', expand.get('coefficient', ''), 'Thermal Expansion'])
                    writer.writerow(['参考温度 (°C)', expand.get('reference_temp', ''), 'Reference Temperature'])

                self._write_flow_stress_csv(writer, material_data)
            return True
        except Exception as exc:
            print(f'导出CSV失败: {exc}')
            return False

    def export_to_txt(self, material_data: Dict[str, Any], output_path: str) -> bool:
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write('=' * 80 + '\n')
                file.write('CAE材料属性数据报告\nCAE Material Property Data Report\n')
                file.write('=' * 80 + '\n\n')
                if 'MTNAME' in material_data:
                    mtname = material_data['MTNAME']
                    file.write(f"材料名称: {mtname.get('name', 'N/A')}\n")
                    file.write(f"材料编号: {mtname.get('id', 'N/A')}\n")
                if 'UNIT' in material_data:
                    file.write(f"单位系统: {material_data['UNIT']}\n")
                file.write('\n材料属性:\n')
                for key, value in material_data.items():
                    if key != 'FSTRES':
                        file.write(f'{key}: {value}\n')
                self._write_flow_stress_txt(file, material_data)
                file.write('\n' + '=' * 80 + '\n')
                file.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            return True
        except Exception as exc:
            print(f'导出TXT失败: {exc}')
            return False

    def batch_export(self, material_data: Dict[str, Any], output_base_path: str, formats: List[str] = None) -> Dict[str, bool]:
        formats = formats or ['json', 'csv', 'txt']
        results = {}
        for fmt in formats:
            method = getattr(self, f'export_to_{fmt}', None)
            results[fmt] = bool(method and method(material_data, f'{output_base_path}.{fmt}'))
        return results

    def _write_property_group(self, writer, title: str, material_data: Dict[str, Any], props: Dict[str, Any]):
        writer.writerow([])
        writer.writerow([title])
        for key, (cn_name, en_name) in props.items():
            if key in material_data:
                data = material_data[key]
                value = data.get('value', '') if isinstance(data, dict) else data
                writer.writerow([cn_name, value, en_name])

    def _write_flow_stress_csv(self, writer, material_data: Dict[str, Any]):
        if 'FSTRES' not in material_data:
            return
        fstres = material_data['FSTRES']
        strain_data = fstres.get('strain_data', [])
        writer.writerow([])
        writer.writerow(['四、流动应力数据'])
        writer.writerow(['应变点数', fstres.get('num_strain', '')])
        writer.writerow(['应变率组数', fstres.get('num_rate', '')])
        writer.writerow(['温度点数', fstres.get('num_temp', '')])
        writer.writerow(['温度/应变率/应变'] + [f'{strain:.6g}' for strain in strain_data])
        for temp, rate, stress_row in self._iter_flow_stress_rows(fstres):
            label = f'{temp:g}' if rate is None else f'{temp:g} / {rate:g}'
            writer.writerow([label] + stress_row)

    def _write_flow_stress_txt(self, file, material_data: Dict[str, Any]):
        if 'FSTRES' not in material_data:
            return
        fstres = material_data['FSTRES']
        file.write('\n流动应力数据:\n')
        for temp, rate, stress_row in self._iter_flow_stress_rows(fstres):
            label = f'T={temp:g}°C' if rate is None else f'T={temp:g}°C, rate={rate:g}/s'
            file.write(f'{label}: {stress_row}\n')

    def _iter_flow_stress_rows(self, fstres: Dict[str, Any]):
        temp_data = fstres.get('temperature_data', [])
        rate_data = fstres.get('strain_rate_data', []) or [None]
        stress_data = fstres.get('stress_data', [])
        is_3d = bool(stress_data and isinstance(stress_data[0], list) and stress_data[0] and isinstance(stress_data[0][0], list))
        if is_3d:
            for temp, temp_block in zip(temp_data, stress_data):
                for rate, stress_row in zip(rate_data, temp_block):
                    yield temp, rate, stress_row
        else:
            for temp, stress_row in zip(temp_data, stress_data):
                yield temp, None, stress_row
