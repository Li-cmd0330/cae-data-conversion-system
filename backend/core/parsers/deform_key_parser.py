"""
DEFORM Key文件解析器模块
用于解析DEFORM格式的key文件中的材料属性数据
"""
import re
from typing import Dict, List, Any, Optional


class DEFORMKeyParser:
    """DEFORM Key文件解析器类"""
    
    def __init__(self, file_path: str):
        """
        初始化解析器
        
        Args:
            file_path: key文件路径
        """
        self.file_path = file_path
        self.content = ""
        self.material_data = {}
        
    def read_file(self) -> str:
        """读取key文件内容"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return self.content
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(self.file_path, 'r', encoding='gbk') as f:
                self.content = f.read()
            return self.content
    
    def parse(self) -> Dict[str, Any]:
        """
        解析key文件
        
        Returns:
            包含材料属性的字典
        """
        if not self.content:
            self.read_file()
        
        lines = self.content.split('\n')
        i = 0
        current_keyword = None
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过注释行和空行
            if not line or line.startswith('*'):
                i += 1
                continue
            
            # 检测关键字
            parts = line.split()
            if parts:
                keyword = parts[0]
                
                if keyword == 'UNIT':
                    self.material_data['UNIT'] = int(parts[1]) if len(parts) > 1 else None
                
                elif keyword == 'MTNAME':
                    material_id = int(parts[1]) if len(parts) > 1 else None
                    i += 1
                    if i < len(lines):
                        material_name = lines[i].strip()
                        self.material_data['MTNAME'] = {
                            'id': material_id,
                            'name': material_name
                        }
                
                elif keyword == 'FRAE2H':
                    self.material_data['FRAE2H'] = {
                        'id': int(parts[1]) if len(parts) > 1 else None,
                        'value': float(parts[2]) if len(parts) > 2 else None
                    }
                
                elif keyword == 'FPERV':
                    self.material_data['FPERV'] = {
                        'id': int(parts[1]) if len(parts) > 1 else None,
                        'value': float(parts[2]) if len(parts) > 2 else None
                    }
                
                elif keyword == 'FRCMOD':
                    # FRCMOD 格式：FRCMOD id damage_model D1 D2 D3 D4 D5 [epsilon0 Tr Tm]
                    # damage_model: 0=归一化Cockcroft-Latham, 1=Cockcroft-Latham, 其他=Johnson-Cook
                    # Johnson-Cook损伤模型参数: D1, D2, D3, D4, D5, epsilon0, Tr, Tm
                    self.material_data['FRCMOD'] = {
                        'id': int(parts[1]) if len(parts) > 1 else None,
                        'damage_model': int(parts[2]) if len(parts) > 2 else None,
                        'D1': float(parts[3]) if len(parts) > 3 else None,
                        'D2': float(parts[4]) if len(parts) > 4 else None,
                        'D3': float(parts[5]) if len(parts) > 5 else None,
                        'D4': float(parts[6]) if len(parts) > 6 else None,
                        'D5': float(parts[7]) if len(parts) > 7 else None,
                        'epsilon0': float(parts[8]) if len(parts) > 8 else None,
                        'Tr': float(parts[9]) if len(parts) > 9 else None,
                        'Tm': float(parts[10]) if len(parts) > 10 else None,
                        # 保留旧的value字段以兼容Cockcroft-Latham模型
                        'value': float(parts[3]) if len(parts) > 3 else None
                    }
                
                elif keyword == 'FSTRES':
                    # 解析流动应力数据
                    fstres_data = self._parse_fstres(lines, i)
                    self.material_data['FSTRES'] = fstres_data
                    # 跳过已解析的行
                    i += fstres_data.get('lines_read', 0)
                
                elif keyword == 'YOUNG':
                    # 解析杨氏模量数据（支持多种格式）
                    young_data = self._parse_property_with_curve(lines, i, 'YOUNG')
                    self.material_data['YOUNG'] = young_data
                    i += young_data.get('lines_read', 0)
                
                elif keyword == 'POISON':
                    # 解析泊松比数据（支持多种格式）
                    poison_data = self._parse_property_with_curve(lines, i, 'POISON')
                    self.material_data['POISON'] = poison_data
                    i += poison_data.get('lines_read', 0)
                
                elif keyword == 'EXPAND':
                    # 解析热膨胀系数数据（支持多种格式）
                    expand_data = self._parse_expand_property(lines, i)
                    self.material_data['EXPAND'] = expand_data
                    i += expand_data.get('lines_read', 0)
                
                elif keyword == 'THRCND':
                    # 解析热传导系数数据（支持多种格式）
                    thrcnd_data = self._parse_property_with_curve(lines, i, 'THRCND')
                    self.material_data['THRCND'] = thrcnd_data
                    i += thrcnd_data.get('lines_read', 0)
                
                elif keyword == 'HEATCP':
                    # 解析比热容数据（支持多种格式）
                    heatcp_data = self._parse_heatcp_property(lines, i)
                    self.material_data['HEATCP'] = heatcp_data
                    i += heatcp_data.get('lines_read', 0)
                
                elif keyword == 'EMSVTY':
                    # 解析发射率数据（支持多种格式）
                    emsvty_data = self._parse_property_with_curve(lines, i, 'EMSVTY')
                    self.material_data['EMSVTY'] = emsvty_data
                    i += emsvty_data.get('lines_read', 0)
                
                elif keyword == 'MASDEN':
                    # 解析密度数据（支持多种格式）
                    masden_data = self._parse_property_with_curve(lines, i, 'MASDEN')
                    self.material_data['MASDEN'] = masden_data
                    i += masden_data.get('lines_read', 0)
                
                elif keyword == 'HDNPHA':
                    self.material_data['HDNPHA'] = {
                        'id': int(parts[1]) if len(parts) > 1 else None,
                        'type': int(parts[2]) if len(parts) > 2 else None,
                        'value': float(parts[3]) if len(parts) > 3 else None
                    }
                
                # 其他关键字的简单处理
                elif keyword in ['MSTMTR', 'CREEP', 'HDNRUL']:
                    self.material_data[keyword] = {
                        'id': int(parts[1]) if len(parts) > 1 else None,
                        'type': int(parts[2]) if len(parts) > 2 else None
                    }
                
                elif keyword in ['DIFCOE', 'ELRST', 'UTSDAT', 'PMEAB', 'PMITT', 'BURGRS', 'ALPHA', 'NDISFM', 'SRFNRG']:
                    self.material_data[keyword] = {
                        'id': int(parts[1]) if len(parts) > 1 else None,
                        'type': int(parts[2]) if len(parts) > 2 else None,
                        'value': float(parts[3]) if len(parts) > 3 else None
                    }
            
            i += 1
        
        return self.material_data
    
    def _parse_fstres(self, lines: List[str], start_index: int) -> Dict[str, Any]:
        """
        解析FSTRES流动应力数据
        
        格式说明：
        1行：FSTRES + 类型
        2行：应变点数k + 应变速率组数m + 温度组数n
        3行：应变值（k个点）
        4行：应变速率值（m组）
        5行：温度值（n组）
        6行起：应力值，共n*m*k个
        顺序：((STRESS(N,M,K), K=1,k), M=1,m), N=1,n)
        即：外层循环温度N，中层循环应变速率M，内层循环应变K
        
        Args:
            lines: 文件行列表
            start_index: 起始行索引
        
        Returns:
            流动应力数据字典
        """
        parts = lines[start_index].strip().split()
        fstres_data = {
            'id': int(parts[1]) if len(parts) > 1 else None,
            'type': int(parts[2]) if len(parts) > 2 else None,
            'strain_data': [],
            'strain_rate_data': [],
            'temperature_data': [],
            'stress_data': [],
            'lines_read': 0
        }
        
        i = start_index + 1
        
        # 读取第2行：k m n
        if i < len(lines):
            line = lines[i].strip()
            if line and not line.startswith('*'):
                params = line.split()
                if len(params) >= 3:
                    fstres_data['num_strain'] = int(params[0])      # k: 应变点数
                    fstres_data['num_rate'] = int(params[1])        # m: 应变速率组数
                    fstres_data['num_temp'] = int(params[2])        # n: 温度组数
                i += 1
        
        num_strain = fstres_data.get('num_strain', 0)
        num_rate = fstres_data.get('num_rate', 0)
        num_temp = fstres_data.get('num_temp', 0)
        
        # 读取第3行：应变值（k个点）
        strain_values = []
        while i < len(lines) and len(strain_values) < num_strain:
            line = lines[i].strip()
            if line and not line.startswith('*'):
                values = line.split()
                strain_values.extend([float(v) for v in values])
                i += 1
            else:
                break
        fstres_data['strain_data'] = strain_values[:num_strain]
        
        # 读取第4行：应变速率值（m组）
        strain_rate_values = []
        while i < len(lines) and len(strain_rate_values) < num_rate:
            line = lines[i].strip()
            if line and not line.startswith('*'):
                values = line.split()
                strain_rate_values.extend([float(v) for v in values])
                i += 1
            else:
                break
        fstres_data['strain_rate_data'] = strain_rate_values[:num_rate]
        
        # 读取第5行：温度值（n组）
        temp_values = []
        while i < len(lines) and len(temp_values) < num_temp:
            line = lines[i].strip()
            if line and not line.startswith('*'):
                values = line.split()
                temp_values.extend([float(v) for v in values])
                i += 1
            else:
                break
        fstres_data['temperature_data'] = temp_values[:num_temp]
        
        # 读取第6行起：应力值，共n*m*k个
        # 顺序：((STRESS(N,M,K), K=1,k), M=1,m), N=1,n)
        # 即：温度N - 应变速率M - 应变K
        total_stress_values = num_temp * num_rate * num_strain
        all_stress_values = []
        
        while i < len(lines) and len(all_stress_values) < total_stress_values:
            line = lines[i].strip()
            if line and not line.startswith('*'):
                # 检查是否遇到下一个关键字
                if line.split()[0] in ['YOUNG', 'POISON', 'EXPAND', 'THRCND', 'HEATCP', 
                                       'EMSVTY', 'MASDEN', 'HDNPHA', 'MSTMTR', 'CREEP',
                                       'DIFCOE', 'ELRST', 'UTSDAT', 'HDNRUL']:
                    break
                values = line.split()
                all_stress_values.extend([float(v) for v in values])
                i += 1
            else:
                i += 1
        
        # 重组应力数据为三维结构：[温度][应变速率][应变]
        stress_3d = []
        idx = 0
        for n in range(num_temp):
            temp_data = []
            for m in range(num_rate):
                rate_data = []
                for k in range(num_strain):
                    if idx < len(all_stress_values):
                        rate_data.append(all_stress_values[idx])
                        idx += 1
                    else:
                        rate_data.append(0.0)
                temp_data.append(rate_data)
            stress_3d.append(temp_data)
        
        fstres_data['stress_data'] = stress_3d
        fstres_data['lines_read'] = i - start_index - 1
        
        
        return fstres_data
    
    def _parse_property_with_curve(self, lines: List[str], start_index: int, keyword: str) -> Dict[str, Any]:
        """
        解析支持温度曲线的材料属性
        
        格式说明：
        Ftype = 0: 常数值
            KEYWORD Material, Ftype, Value
        Ftype = 1: 温度相关曲线
            KEYWORD Material, Ftype, Ndata
            Temp(1), Value(1)
            ...
            Temp(Ndata), Value(Ndata)
        Ftype = 2,3,4: 密度/原子/温度+原子相关（微观结构模块专用）
        
        Args:
            lines: 文件行列表
            start_index: 起始行索引
            keyword: 关键字名称
        
        Returns:
            属性数据字典
        """
        parts = lines[start_index].strip().split()
        property_data = {
            'id': int(parts[1]) if len(parts) > 1 else None,
            'type': int(parts[2]) if len(parts) > 2 else 0,
            'value': None,
            'curve_data': [],
            'lines_read': 0
        }
        
        ftype = property_data['type']
        
        if ftype == 0:
            # 常数值
            if len(parts) > 3:
                property_data['value'] = float(parts[3])
        
        elif ftype == 1:
            # 温度相关曲线
            ndata = int(parts[3]) if len(parts) > 3 else 0
            property_data['ndata'] = ndata
            
            i = start_index + 1
            curve_values = []
            
            while i < len(lines) and len(curve_values) < ndata:
                line = lines[i].strip()
                if line and not line.startswith('*'):
                    # 检查是否遇到下一个关键字
                    if self._is_keyword_line(line):
                        break
                    
                    values = line.split()
                    # 每行格式：Temp Value
                    if len(values) >= 2:
                        try:
                            temp = float(values[0])
                            val = float(values[1])
                            curve_values.append({'temperature': temp, 'value': val})
                        except ValueError:
                            pass
                    i += 1
                else:
                    i += 1
            
            property_data['curve_data'] = curve_values
            property_data['lines_read'] = i - start_index - 1
            
            # 如果有曲线数据，第一个点的值作为默认值
            if curve_values:
                property_data['value'] = curve_values[0]['value']
        
        elif ftype in [2, 3, 4]:
            # 密度/原子/温度+原子相关（微观结构模块）
            # 简化处理：读取参数但不详细解析
            if len(parts) > 3:
                property_data['n1'] = int(parts[3]) if len(parts) > 3 else 0
                property_data['n2'] = int(parts[4]) if len(parts) > 4 else 0
            
            # 跳过后续数据行（具体实现可按需扩展）
            property_data['lines_read'] = 0
        
        return property_data
    
    def _parse_expand_property(self, lines: List[str], start_index: int) -> Dict[str, Any]:
        """
        解析热膨胀系数（EXPAND）
        
        格式说明：
        Ftype = 0: 常数值
            EXPAND Material, Ftype, Expansion, Temp
        Ftype = 1: 温度相关曲线
            EXPAND Material, Ftype, Ndata, Temp
            Temp(1), Expansion(1)
            ...
            Temp(Ndata), Expansion(Ndata)
        
        Args:
            lines: 文件行列表
            start_index: 起始行索引
        
        Returns:
            热膨胀系数数据字典
        """
        parts = lines[start_index].strip().split()
        expand_data = {
            'id': int(parts[1]) if len(parts) > 1 else None,
            'type': int(parts[2]) if len(parts) > 2 else 0,
            'coefficient': None,
            'reference_temp': None,
            'curve_data': [],
            'lines_read': 0
        }
        
        ftype = expand_data['type']
        
        if ftype == 0:
            # 常数值：EXPAND Material, Ftype, Expansion, Temp
            if len(parts) > 3:
                expand_data['coefficient'] = float(parts[3])
            if len(parts) > 4:
                expand_data['reference_temp'] = float(parts[4])
        
        elif ftype == 1:
            # 温度相关曲线：EXPAND Material, Ftype, Ndata, Temp
            ndata = int(parts[3]) if len(parts) > 3 else 0
            if len(parts) > 4:
                expand_data['reference_temp'] = float(parts[4])
            
            expand_data['ndata'] = ndata
            
            i = start_index + 1
            curve_values = []
            
            while i < len(lines) and len(curve_values) < ndata:
                line = lines[i].strip()
                if line and not line.startswith('*'):
                    if self._is_keyword_line(line):
                        break
                    
                    values = line.split()
                    if len(values) >= 2:
                        try:
                            temp = float(values[0])
                            coeff = float(values[1])
                            curve_values.append({'temperature': temp, 'coefficient': coeff})
                        except ValueError:
                            pass
                    i += 1
                else:
                    i += 1
            
            expand_data['curve_data'] = curve_values
            expand_data['lines_read'] = i - start_index - 1
            
            # 如果有曲线数据，第一个点的值作为默认值
            if curve_values:
                expand_data['coefficient'] = curve_values[0]['coefficient']
        
        return expand_data
    
    def _parse_heatcp_property(self, lines: List[str], start_index: int) -> Dict[str, Any]:
        """
        解析比热容（HEATCP）
        
        格式说明：
        Ftype = 0: 常数值
            HEATCP Material, Ftype, HeatCP, DensityFlag
        Ftype = 1: 温度相关曲线
            HEATCP Material, Ftype, Ndata, DensityFlag
            Temp(1), HeatCP(1)
            ...
            Temp(Ndata), HeatCP(Ndata)
        
        Args:
            lines: 文件行列表
            start_index: 起始行索引
        
        Returns:
            比热容数据字典
        """
        parts = lines[start_index].strip().split()
        heatcp_data = {
            'id': int(parts[1]) if len(parts) > 1 else None,
            'type': int(parts[2]) if len(parts) > 2 else 0,
            'value': None,
            'density_flag': None,
            'curve_data': [],
            'lines_read': 0
        }
        
        ftype = heatcp_data['type']
        
        if ftype == 0:
            # 常数值：HEATCP Material, Ftype, HeatCP, DensityFlag
            if len(parts) > 3:
                heatcp_data['value'] = float(parts[3])
            if len(parts) > 4:
                heatcp_data['density_flag'] = int(parts[4])
        
        elif ftype == 1:
            # 温度相关曲线：HEATCP Material, Ftype, Ndata, DensityFlag
            ndata = int(parts[3]) if len(parts) > 3 else 0
            if len(parts) > 4:
                heatcp_data['density_flag'] = int(parts[4])
            
            heatcp_data['ndata'] = ndata
            
            i = start_index + 1
            curve_values = []
            
            while i < len(lines) and len(curve_values) < ndata:
                line = lines[i].strip()
                if line and not line.startswith('*'):
                    if self._is_keyword_line(line):
                        break
                    
                    values = line.split()
                    if len(values) >= 2:
                        try:
                            temp = float(values[0])
                            heatcp = float(values[1])
                            curve_values.append({'temperature': temp, 'value': heatcp})
                        except ValueError:
                            pass
                    i += 1
                else:
                    i += 1
            
            heatcp_data['curve_data'] = curve_values
            heatcp_data['lines_read'] = i - start_index - 1
            
            # 如果有曲线数据，第一个点的值作为默认值
            if curve_values:
                heatcp_data['value'] = curve_values[0]['value']
        
        return heatcp_data
    
    def _is_keyword_line(self, line: str) -> bool:
        """
        判断是否为关键字行
        
        Args:
            line: 待判断的行
        
        Returns:
            是否为关键字行
        """
        keywords = [
            'YOUNG', 'POISON', 'EXPAND', 'THRCND', 'HEATCP', 
            'EMSVTY', 'MASDEN', 'HDNPHA', 'MSTMTR', 'CREEP',
            'DIFCOE', 'ELRST', 'UTSDAT', 'HDNRUL', 'FSTRES',
            'FRAE2H', 'FPERV', 'FRCMOD', 'MTNAME', 'UNIT'
        ]
        
        parts = line.split()
        if parts and parts[0] in keywords:
            return True
        return False
    
    def get_material_name(self) -> Optional[str]:
        """获取材料名称"""
        if 'MTNAME' in self.material_data:
            return self.material_data['MTNAME'].get('name')
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """将解析结果转换为字典格式"""
        return self.material_data


if __name__ == "__main__":
    # 测试代码
    test_content = """*
UNIT         1
*
*  Property Data of Material     1
*
MTNAME       1
AL-5083,COLD[70F(20C)]
FRAE2H       1  9.0000000E-001
YOUNG        1       0  6.8900000E+004
POISON       1       0  3.3000000E-001
"""
    
    # 创建测试文件
    with open('test_key.key', 'w') as f:
        f.write(test_content)
    
    parser = DEFORMKeyParser('test_key.key')
    result = parser.parse()
    
    print("解析结果：")
    for key, value in result.items():
        print(f"{key}: {value}")
