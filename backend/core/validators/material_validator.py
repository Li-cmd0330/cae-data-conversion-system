"""
数据验证模块
用于验证材料属性数据的合理性和完整性
"""
from typing import Dict, Any, List, Tuple
import warnings


class DataValidator:
    """数据验证器类"""
    
    # 定义各属性的合理范围（基于工程经验）
    PROPERTY_RANGES = {
        'YOUNG': (1000, 500000, 'MPa'),  # 杨氏模量: 1-500 GPa
        'POISON': (0.0, 0.5, ''),  # 泊松比: 0-0.5
        'THRCND': (0.1, 500, 'W/m·K'),  # 热传导系数
        'HEATCP': (0.1, 10, 'J/kg·K'),  # 比热容
        'EMSVTY': (0.0, 1.0, ''),  # 发射率: 0-1
        'MASDEN': (1e-10, 1e-7, 'kg/mm³'),  # 密度
        'EXPAND': (1e-7, 1e-4, '1/°C'),  # 热膨胀系数
        'FRAE2H': (0.0, 1.0, ''),  # 摩擦因子
        'FPERV': (0.0, 1.0, ''),  # 摩擦系数
    }
    
    # 必需的基本属性
    REQUIRED_PROPERTIES = ['MTNAME', 'UNIT']
    
    # 推荐的力学属性
    RECOMMENDED_MECHANICAL = ['YOUNG', 'POISON']
    
    # 推荐的热学属性
    RECOMMENDED_THERMAL = ['THRCND', 'HEATCP', 'MASDEN']
    
    def __init__(self):
        """初始化验证器"""
        self.warnings = []
        self.errors = []
        self.info = []
        
    def validate(self, material_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str], List[str]]:
        """
        验证材料数据
        
        Args:
            material_data: 材料数据字典
            
        Returns:
            (是否通过验证, 错误列表, 警告列表, 信息列表)
        """
        self.warnings = []
        self.errors = []
        self.info = []
        
        # 1. 检查必需属性
        self._check_required_properties(material_data)
        
        # 2. 检查数值范围
        self._check_value_ranges(material_data)
        
        # 3. 检查推荐属性
        self._check_recommended_properties(material_data)
        
        # 4. 检查流动应力数据
        self._check_flow_stress_data(material_data)
        
        # 5. 检查数据一致性
        self._check_data_consistency(material_data)
        
        # 6. 生成完整性报告
        self._generate_completeness_report(material_data)
        
        # 如果有严重错误,返回False
        is_valid = len(self.errors) == 0
        
        return is_valid, self.errors, self.warnings, self.info
    
    def _check_required_properties(self, material_data: Dict[str, Any]):
        """检查必需属性"""
        for prop in self.REQUIRED_PROPERTIES:
            if prop not in material_data:
                self.errors.append(f"❌ 缺少必需属性: {prop}")
            elif not material_data[prop]:
                self.errors.append(f"❌ 必需属性为空: {prop}")
        
        # 检查材料名称
        if 'MTNAME' in material_data:
            mtname = material_data['MTNAME']
            if isinstance(mtname, dict):
                name = mtname.get('name', '')
                if not name or name.strip() == '':
                    self.warnings.append("⚠️ 材料名称为空")
    
    def _check_value_ranges(self, material_data: Dict[str, Any]):
        """检查数值范围"""
        for prop, (min_val, max_val, unit) in self.PROPERTY_RANGES.items():
            if prop in material_data:
                data = material_data[prop]
                
                # 获取数值
                if isinstance(data, dict):
                    if 'value' in data:
                        value = data['value']
                    elif 'coefficient' in data:  # 针对EXPAND
                        value = data['coefficient']
                    else:
                        continue
                else:
                    value = data
                
                # 检查范围
                if value < min_val or value > max_val:
                    unit_str = f" {unit}" if unit else ""
                    self.warnings.append(
                        f"⚠️ {prop} 数值异常: {value:.6e}{unit_str} "
                        f"(正常范围: {min_val:.6e}-{max_val:.6e}{unit_str})"
                    )
                else:
                    self.info.append(f"✓ {prop} 数值正常")
    
    def _check_recommended_properties(self, material_data: Dict[str, Any]):
        """检查推荐属性"""
        # 检查力学属性
        missing_mech = [p for p in self.RECOMMENDED_MECHANICAL if p not in material_data]
        if missing_mech:
            self.warnings.append(f"⚠️ 缺少推荐的力学属性: {', '.join(missing_mech)}")
        
        # 检查热学属性
        missing_thermal = [p for p in self.RECOMMENDED_THERMAL if p not in material_data]
        if missing_thermal:
            self.warnings.append(f"⚠️ 缺少推荐的热学属性: {', '.join(missing_thermal)}")
    
    def _check_flow_stress_data(self, material_data: Dict[str, Any]):
        """检查流动应力数据"""
        if 'FSTRES' not in material_data:
            self.info.append("ℹ️ 未提供流动应力数据（可选）")
            return
        
        fstres = material_data['FSTRES']
        
        # 检查数据点数
        num_strain = fstres.get('num_strain', 0)
        num_temp = fstres.get('num_temp', 0)
        
        if num_strain < 2:
            self.warnings.append("⚠️ 流动应力数据: 应变点数过少（建议≥3）")
        
        if num_temp < 2:
            self.warnings.append("⚠️ 流动应力数据: 温度点数过少（建议≥2）")
        
        # 检查数据完整性
        strain_data = fstres.get('strain_data', [])
        temp_data = fstres.get('temperature_data', [])
        stress_data = fstres.get('stress_data', [])
        
        if len(strain_data) != num_strain:
            self.errors.append(f"❌ 流动应力数据: 应变数据点数不匹配 (期望{num_strain}, 实际{len(strain_data)})")
        
        if len(temp_data) != num_temp:
            self.errors.append(f"❌ 流动应力数据: 温度数据点数不匹配 (期望{num_temp}, 实际{len(temp_data)})")
        
        if len(stress_data) != num_temp:
            self.errors.append(f"❌ 流动应力数据: 应力矩阵温度维度不匹配 (期望{num_temp}, 实际{len(stress_data)})")
        else:
            num_rate = fstres.get('num_rate', len(fstres.get('strain_rate_data', [])) or 1)
            is_3d = bool(stress_data and isinstance(stress_data[0], list) and stress_data[0] and isinstance(stress_data[0][0], list))
            for i, temp_block in enumerate(stress_data):
                if is_3d:
                    if len(temp_block) != num_rate:
                        self.errors.append(
                            f"❌ 流动应力数据: 第{i+1}个温度块应变率组数不匹配 "
                            f"(期望{num_rate}, 实际{len(temp_block)})"
                        )
                    for r, row in enumerate(temp_block):
                        if len(row) != num_strain:
                            self.errors.append(
                                f"❌ 流动应力数据: 第{i+1}个温度、第{r+1}个应变率的数据点数不匹配 "
                                f"(期望{num_strain}, 实际{len(row)})"
                            )
                elif len(temp_block) != num_strain:
                    self.errors.append(
                        f"❌ 流动应力数据: 第{i+1}行应力数据点数不匹配 "
                        f"(期望{num_strain}, 实际{len(temp_block)})"
                    )
        
        # 检查应变值单调性
        if len(strain_data) > 1:
            if not all(strain_data[i] < strain_data[i+1] for i in range(len(strain_data)-1)):
                self.warnings.append("⚠️ 流动应力数据: 应变值不是单调递增的")
        
        # 检查温度值单调性
        if len(temp_data) > 1:
            if not all(temp_data[i] < temp_data[i+1] for i in range(len(temp_data)-1)):
                self.warnings.append("⚠️ 流动应力数据: 温度值不是单调递增的")
        
        # 检查应力值合理性
        is_3d = bool(stress_data and isinstance(stress_data[0], list) and stress_data[0] and isinstance(stress_data[0][0], list))
        for i, temp_block in enumerate(stress_data):
            rows = temp_block if is_3d else [temp_block]
            for r, row in enumerate(rows):
                for j, stress in enumerate(row):
                    if stress < 0:
                        self.errors.append(f"❌ 流动应力数据: 应力值不能为负 (位置[{i},{r},{j}]={stress})")
                    elif stress > 10000:  # 10 GPa
                        self.warnings.append(f"⚠️ 流动应力数据: 应力值异常大 (位置[{i},{r},{j}]={stress} MPa)")
        
        if not self.errors:
            self.info.append(f"✓ 流动应力数据完整 ({num_strain}×{num_temp}矩阵)")
    
    def _check_data_consistency(self, material_data: Dict[str, Any]):
        """检查数据一致性"""
        # 检查泊松比和杨氏模量的物理关系
        if 'YOUNG' in material_data and 'POISON' in material_data:
            young = material_data['YOUNG'].get('value', 0)
            poison = material_data['POISON'].get('value', 0)
            
            # 对于各向同性材料，泊松比通常在0.2-0.4之间
            if young > 0 and (poison < 0.15 or poison > 0.45):
                self.info.append(f"ℹ️ 泊松比({poison:.3f})不在常见范围(0.15-0.45)，请确认材料特性")
        
        # 检查热膨胀系数和参考温度
        if 'EXPAND' in material_data:
            expand = material_data['EXPAND']
            ref_temp = expand.get('reference_temp', None)
            if ref_temp is None:
                self.warnings.append("⚠️ 热膨胀系数缺少参考温度")
    
    def _generate_completeness_report(self, material_data: Dict[str, Any]):
        """生成完整性报告"""
        # 统计属性数量
        all_possible_props = [
            'MTNAME', 'UNIT', 'YOUNG', 'POISON', 'THRCND', 'HEATCP', 
            'MASDEN', 'EMSVTY', 'EXPAND', 'FRAE2H', 'FPERV', 'FSTRES',
            'HDNPHA', 'DIFCOE', 'ELRST', 'UTSDAT'
        ]
        
        present_props = [p for p in all_possible_props if p in material_data]
        completeness = (len(present_props) / len(all_possible_props)) * 100
        
        self.info.append(f"📊 数据完整度: {completeness:.1f}% ({len(present_props)}/{len(all_possible_props)}项)")
        
        # 按类别统计
        basic_props = ['MTNAME', 'UNIT']
        mechanical_props = ['YOUNG', 'POISON', 'FRAE2H', 'FPERV', 'FSTRES']
        thermal_props = ['THRCND', 'HEATCP', 'MASDEN', 'EMSVTY', 'EXPAND']
        
        basic_count = sum(1 for p in basic_props if p in material_data)
        mech_count = sum(1 for p in mechanical_props if p in material_data)
        thermal_count = sum(1 for p in thermal_props if p in material_data)
        
        self.info.append(f"  - 基本信息: {basic_count}/{len(basic_props)}")
        self.info.append(f"  - 力学性能: {mech_count}/{len(mechanical_props)}")
        self.info.append(f"  - 热学性能: {thermal_count}/{len(thermal_props)}")
    
    def get_validation_report(self) -> str:
        """
        获取验证报告文本
        
        Returns:
            格式化的验证报告
        """
        report = []
        report.append("=" * 60)
        report.append("数据验证报告 | Data Validation Report")
        report.append("=" * 60)
        
        if self.errors:
            report.append("\n【严重错误】")
            report.extend(self.errors)
        
        if self.warnings:
            report.append("\n【警告信息】")
            report.extend(self.warnings)
        
        if self.info:
            report.append("\n【验证信息】")
            report.extend(self.info)
        
        if not self.errors and not self.warnings:
            report.append("\n✅ 数据验证通过！所有检查项均正常。")
        elif not self.errors:
            report.append("\n✅ 数据验证通过（存在一些建议项）。")
        else:
            report.append("\n❌ 数据验证失败，请修正错误后重试。")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    @staticmethod
    def get_property_info(property_name: str) -> Dict[str, Any]:
        """
        获取属性信息和建议
        
        Args:
            property_name: 属性名称
            
        Returns:
            属性信息字典
        """
        property_info = {
            'YOUNG': {
                'name_cn': '杨氏模量',
                'name_en': "Young's Modulus",
                'unit': 'MPa',
                'typical_range': '1,000 - 500,000',
                'description': '材料抵抗弹性变形的能力',
                'examples': {
                    '钢': '200,000 MPa',
                    '铝合金': '70,000 MPa',
                    '钛合金': '110,000 MPa'
                }
            },
            'POISON': {
                'name_cn': '泊松比',
                'name_en': "Poisson's Ratio",
                'unit': '',
                'typical_range': '0.0 - 0.5',
                'description': '材料横向变形与纵向变形的比值',
                'examples': {
                    '钢': '0.30',
                    '铝合金': '0.33',
                    '橡胶': '0.50'
                }
            },
            'THRCND': {
                'name_cn': '热传导系数',
                'name_en': 'Thermal Conductivity',
                'unit': 'W/m·K',
                'typical_range': '0.1 - 500',
                'description': '材料传导热量的能力',
                'examples': {
                    '铜': '400 W/m·K',
                    '铝': '200 W/m·K',
                    '钢': '50 W/m·K'
                }
            },
            # 可以继续添加更多属性...
        }
        
        return property_info.get(property_name, {
            'name_cn': property_name,
            'name_en': property_name,
            'description': '无详细信息'
        })


if __name__ == "__main__":
    # 测试代码
    test_data = {
        'UNIT': 1,
        'MTNAME': {'id': 1, 'name': 'AL-5083,COLD[70F(20C)]'},
        'YOUNG': {'id': 1, 'type': 0, 'value': 68900.0},
        'POISON': {'id': 1, 'type': 0, 'value': 0.33},
        'THRCND': {'id': 1, 'type': 0, 'value': 180.2},
        'HEATCP': {'id': 1, 'type': 0, 'value': 2.433},
        'MASDEN': {'id': 1, 'type': 0, 'value': 2.66e-9},
        'FSTRES': {
            'num_strain': 3,
            'num_temp': 2,
            'strain_data': [0.0, 0.5, 1.0],
            'temperature_data': [20.0, 100.0],
            'stress_data': [
                [100, 150, 180],
                [90, 140, 170]
            ]
        }
    }
    
    validator = DataValidator()
    is_valid, errors, warnings, info = validator.validate(test_data)
    
    print(validator.get_validation_report())
    print(f"\n验证结果: {'通过' if is_valid else '失败'}")
