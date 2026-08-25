"""
智能数据修复器
检测缺失值、异常值、单位错误，提供修复建议
"""
import numpy as np


class IntelligentDataRepair:
    """智能数据修复器"""
    
    # 材料参数的典型范围
    PARAMETER_RANGES = {
        'YOUNG': {  # 杨氏模量 (MPa)
            'aluminum': (60000, 80000),
            'steel': (190000, 210000),
            'titanium': (100000, 120000),
            'copper': (110000, 130000),
            'superalloy': (180000, 220000)
        },
        'POISON': {  # 泊松比
            'all': (0.25, 0.35)
        },
        'MASDEN': {  # 密度 (kg/m³)
            'aluminum': (2500, 2900),
            'steel': (7800, 8100),
            'titanium': (4400, 4600),
            'copper': (8800, 9000),
            'superalloy': (8000, 9000)
        },
        'THRCND': {  # 热导率 (W/m·K)
            'aluminum': (150, 250),
            'steel': (40, 60),
            'titanium': (15, 25),
            'copper': (350, 400),
            'superalloy': (10, 20)
        },
        'HEATCP': {  # 比热容 (J/kg·K)
            'aluminum': (850, 950),
            'steel': (450, 550),
            'titanium': (500, 600),
            'copper': (380, 420),
            'superalloy': (400, 500)
        },
        'EXPAND': {  # 热膨胀系数 (1/K)
            'aluminum': (2.0e-5, 2.5e-5),
            'steel': (1.0e-5, 1.3e-5),
            'titanium': (8.0e-6, 9.5e-6),
            'copper': (1.6e-5, 1.8e-5),
            'superalloy': (1.2e-5, 1.5e-5)
        }
    }
    
    # 典型默认值
    TYPICAL_VALUES = {
        'POISON': 0.3,
        'EXPAND': 1.2e-5
    }
    
    def analyze_and_repair(self, material_data, material_type='unknown'):
        """
        分析材料数据并提供修复建议
        
        Args:
            material_data: 材料数据字典
            material_type: 材料类型
            
        Returns:
            {
                'issues': [问题列表],
                'suggestions': {参数: 建议值},
                'confidence': {参数: 置信度},
                'auto_fixable': [可自动修复的参数]
            }
        """
        issues = []
        suggestions = {}
        confidence = {}
        auto_fixable = []
        
        # 1. 检测缺失值
        missing = self._detect_missing(material_data)
        for param in missing:
            issues.append({
                'type': 'missing',
                'parameter': param,
                'severity': 'high' if param in ['YOUNG', 'POISON', 'MASDEN'] else 'medium',
                'message': f'{param} 参数缺失'
            })
            
            # 提供建议值
            suggestion = self._suggest_missing_value(param, material_type, material_data)
            if suggestion:
                suggestions[param] = suggestion['value']
                confidence[param] = suggestion['confidence']
                if suggestion['confidence'] > 0.6:
                    auto_fixable.append(param)
        
        # 2. 检测异常值
        anomalies = self._detect_anomalies(material_data, material_type)
        for anomaly in anomalies:
            issues.append({
                'type': 'anomaly',
                'parameter': anomaly['parameter'],
                'current_value': anomaly['value'],
                'expected_range': anomaly['expected_range'],
                'severity': anomaly['severity'],
                'message': anomaly['message']
            })
            
            # 提供修正建议
            suggestion = self._suggest_correction(anomaly, material_type)
            if suggestion:
                suggestions[anomaly['parameter']] = suggestion['value']
                confidence[anomaly['parameter']] = suggestion['confidence']
        
        # 3. 检测单位不一致
        unit_issues = self._detect_unit_inconsistency(material_data)
        for issue in unit_issues:
            issues.append({
                'type': 'unit_inconsistency',
                'parameter': issue['parameter'],
                'detected_unit': issue['detected_unit'],
                'expected_unit': issue['expected_unit'],
                'severity': 'high',
                'message': issue['message']
            })
            
            # 自动转换单位
            suggestions[issue['parameter']] = issue['converted_value']
            confidence[issue['parameter']] = 0.95
            auto_fixable.append(issue['parameter'])
        
        # 4. 检查数据一致性
        consistency_issues = self._check_consistency(material_data)
        issues.extend(consistency_issues)
        
        return {
            'issues': issues,
            'suggestions': suggestions,
            'confidence': confidence,
            'auto_fixable': list(set(auto_fixable)),  # 去重
            'total_issues': len(issues),
            'critical_issues': len([i for i in issues if i['severity'] == 'high']),
            'has_issues': len(issues) > 0
        }
    
    def _detect_missing(self, data):
        """检测缺失的必需参数"""
        required_params = ['YOUNG', 'POISON', 'MASDEN']
        missing = []
        
        for param in required_params:
            if param not in data or data[param] is None:
                missing.append(param)
            elif isinstance(data[param], dict):
                if 'value' not in data[param] or data[param]['value'] is None:
                    missing.append(param)
        
        return missing
    
    def _suggest_missing_value(self, param, material_type, existing_data):
        """为缺失参数建议值"""
        
        # 方法1: 基于材料类型的典型值
        if material_type != 'unknown' and param in self.PARAMETER_RANGES:
            if material_type in self.PARAMETER_RANGES[param]:
                range_min, range_max = self.PARAMETER_RANGES[param][material_type]
                typical_value = (range_min + range_max) / 2
                
                return {
                    'value': typical_value,
                    'confidence': 0.7,
                    'method': 'typical_value',
                    'source': f'{material_type}的典型值'
                }
            elif 'all' in self.PARAMETER_RANGES[param]:
                range_min, range_max = self.PARAMETER_RANGES[param]['all']
                typical_value = (range_min + range_max) / 2
                
                return {
                    'value': typical_value,
                    'confidence': 0.6,
                    'method': 'typical_value',
                    'source': '通用典型值'
                }
        
        # 方法2: 使用默认值
        if param in self.TYPICAL_VALUES:
            return {
                'value': self.TYPICAL_VALUES[param],
                'confidence': 0.5,
                'method': 'default',
                'source': '通用默认值'
            }
        
        return None
    
    def _detect_anomalies(self, data, material_type):
        """检测异常值"""
        anomalies = []
        
        for param, value in data.items():
            if param not in self.PARAMETER_RANGES:
                continue
            
            # 提取数值
            numeric_value = self._extract_numeric(value)
            if numeric_value is None:
                continue
            
            # 检查是否在合理范围内
            ranges = self.PARAMETER_RANGES[param]
            expected_range = None
            
            if material_type in ranges:
                expected_range = ranges[material_type]
            elif 'all' in ranges:
                expected_range = ranges['all']
            
            if expected_range:
                min_val, max_val = expected_range
                
                # 严重偏离（超出范围50%以上）
                if numeric_value < min_val * 0.5 or numeric_value > max_val * 1.5:
                    anomalies.append({
                        'parameter': param,
                        'value': numeric_value,
                        'expected_range': expected_range,
                        'severity': 'high',
                        'message': f'{param}值({numeric_value:.2f})严重偏离正常范围[{min_val:.2f}, {max_val:.2f}]'
                    })
                # 轻微偏离
                elif numeric_value < min_val or numeric_value > max_val:
                    anomalies.append({
                        'parameter': param,
                        'value': numeric_value,
                        'expected_range': expected_range,
                        'severity': 'medium',
                        'message': f'{param}值({numeric_value:.2f})略微偏离正常范围[{min_val:.2f}, {max_val:.2f}]'
                    })
        
        return anomalies
    
    def _detect_unit_inconsistency(self, data):
        """检测单位不一致"""
        issues = []
        
        # 检查杨氏模量单位（应该是MPa）
        if 'YOUNG' in data:
            young = self._extract_numeric(data['YOUNG'])
            if young and young < 1000:  # 可能是GPa
                issues.append({
                    'parameter': 'YOUNG',
                    'detected_unit': 'GPa',
                    'expected_unit': 'MPa',
                    'converted_value': young * 1000,
                    'message': f'杨氏模量单位可能是GPa，建议转换: {young} GPa → {young * 1000} MPa'
                })
        
        # 检查密度单位（应该是kg/m³）
        if 'MASDEN' in data:
            masden = self._extract_numeric(data['MASDEN'])
            if masden and masden < 100:  # 可能是g/cm³
                issues.append({
                    'parameter': 'MASDEN',
                    'detected_unit': 'g/cm³',
                    'expected_unit': 'kg/m³',
                    'converted_value': masden * 1000,
                    'message': f'密度单位可能是g/cm³，建议转换: {masden} g/cm³ → {masden * 1000} kg/m³'
                })
        
        return issues
    
    def _check_consistency(self, data):
        """检查数据一致性"""
        issues = []
        
        # 检查泊松比范围
        poison = self._extract_numeric(data.get('POISON'))
        if poison:
            if poison < 0 or poison > 0.5:
                issues.append({
                    'type': 'consistency',
                    'parameter': 'POISON',
                    'severity': 'high',
                    'message': f'泊松比({poison})超出物理意义范围[0, 0.5]'
                })
        
        # 检查密度是否为正
        masden = self._extract_numeric(data.get('MASDEN'))
        if masden and masden <= 0:
            issues.append({
                'type': 'consistency',
                'parameter': 'MASDEN',
                'severity': 'high',
                'message': f'密度({masden})必须为正值'
            })
        
        # 检查杨氏模量是否为正
        young = self._extract_numeric(data.get('YOUNG'))
        if young and young <= 0:
            issues.append({
                'type': 'consistency',
                'parameter': 'YOUNG',
                'severity': 'high',
                'message': f'杨氏模量({young})必须为正值'
            })
        
        return issues
    
    def _suggest_correction(self, anomaly, material_type):
        """建议异常值的修正"""
        param = anomaly['parameter']
        expected_range = anomaly['expected_range']
        
        # 使用范围中值作为建议
        suggested_value = (expected_range[0] + expected_range[1]) / 2
        
        return {
            'value': suggested_value,
            'confidence': 0.6,
            'method': 'range_median',
            'source': f'使用典型范围中值'
        }
    
    def _extract_numeric(self, value):
        """提取数值"""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, dict):
            if 'value' in value:
                return value['value']
            if 'values' in value and value['values']:
                return value['values'][0]
        if isinstance(value, list) and value:
            return value[0]
        return None
    
    def apply_auto_fix(self, material_data, repair_result):
        """自动应用修复"""
        fixed_data = material_data.copy()
        applied_fixes = []
        
        for param in repair_result['auto_fixable']:
            if param in repair_result['suggestions']:
                old_value = fixed_data.get(param)
                new_value = repair_result['suggestions'][param]
                fixed_data[param] = new_value
                
                applied_fixes.append({
                    'parameter': param,
                    'old_value': old_value,
                    'new_value': new_value,
                    'confidence': repair_result['confidence'][param]
                })
        
        return {
            'fixed_data': fixed_data,
            'applied_fixes': applied_fixes,
            'fix_count': len(applied_fixes)
        }
