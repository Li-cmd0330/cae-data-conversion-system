"""
智能材料分类器
根据文件名和材料属性自动识别材料类型
"""


class MaterialClassifier:
    """智能材料分类器"""
    
    # 材料类型特征库
    MATERIAL_PATTERNS = {
        'aluminum': {
            'keywords': ['AL', 'ALUMINUM', 'ALU', '6061', '7075', '2024', '5052'],
            'density_range': (2500, 2900),
            'young_range': (60000, 80000),
            'tags': ['铝合金', '轻质', '耐腐蚀'],
            'icon': '🔷',
            'name_cn': '铝合金'
        },
        'steel': {
            'keywords': ['AISI', 'STEEL', 'ST', 'SS', '1015', '1045', '4140'],
            'density_range': (7800, 8100),
            'young_range': (190000, 210000),
            'tags': ['钢材', '高强度'],
            'icon': '⚙️',
            'name_cn': '钢材'
        },
        'superalloy': {
            'keywords': ['INCONEL', 'INCOLOY', 'HASTELLOY', '625', '718', '901'],
            'density_range': (8000, 9000),
            'young_range': (180000, 220000),
            'tags': ['高温合金', '耐高温', '航空航天'],
            'icon': '🔥',
            'name_cn': '高温合金'
        },
        'titanium': {
            'keywords': ['TI', 'TITAN', 'TYPE'],
            'density_range': (4400, 4600),
            'young_range': (100000, 120000),
            'tags': ['钛合金', '高强度', '轻质'],
            'icon': '💎',
            'name_cn': '钛合金'
        },
        'copper': {
            'keywords': ['CU', 'COPPER', 'BRASS', 'CUZN', 'C10'],
            'density_range': (8800, 9000),
            'young_range': (110000, 130000),
            'tags': ['铜合金', '导电', '导热'],
            'icon': '🟠',
            'name_cn': '铜合金'
        }
    }
    
    def classify(self, filename, properties):
        """
        智能分类材料
        
        Args:
            filename: 文件名
            properties: 材料属性字典
            
        Returns:
            {
                'type': '材料类型',
                'type_cn': '中文名称',
                'confidence': 0.95,
                'tags': ['标签1', '标签2'],
                'icon': '🔷',
                'method': '识别方法'
            }
        """
        scores = {}
        methods = {}
        
        # 1. 从文件名识别
        filename_upper = filename.upper()
        for mat_type, features in self.MATERIAL_PATTERNS.items():
            score = 0
            matched_keywords = []
            for keyword in features['keywords']:
                if keyword in filename_upper:
                    score += 0.4
                    matched_keywords.append(keyword)
            if score > 0:
                scores[mat_type] = scores.get(mat_type, 0) + score
                methods[mat_type] = f"文件名匹配: {', '.join(matched_keywords)}"
        
        # 2. 从密度识别
        density = self._extract_numeric(properties.get('MASDEN'))
        if density:
            for mat_type, features in self.MATERIAL_PATTERNS.items():
                if 'density_range' in features:
                    min_d, max_d = features['density_range']
                    if min_d <= density <= max_d:
                        scores[mat_type] = scores.get(mat_type, 0) + 0.3
                        if mat_type not in methods:
                            methods[mat_type] = f"密度匹配: {density} kg/m³"
        
        # 3. 从杨氏模量识别
        young = self._extract_numeric(properties.get('YOUNG'))
        if young:
            for mat_type, features in self.MATERIAL_PATTERNS.items():
                if 'young_range' in features:
                    min_y, max_y = features['young_range']
                    if min_y <= young <= max_y:
                        scores[mat_type] = scores.get(mat_type, 0) + 0.3
                        if mat_type not in methods:
                            methods[mat_type] = f"杨氏模量匹配: {young} MPa"
        
        # 选择得分最高的类型
        if scores:
            best_type = max(scores, key=scores.get)
            confidence = min(scores[best_type], 1.0)
            
            if confidence > 0.3:  # 置信度阈值
                features = self.MATERIAL_PATTERNS[best_type]
                return {
                    'type': best_type,
                    'type_cn': features['name_cn'],
                    'confidence': round(confidence, 2),
                    'tags': features['tags'],
                    'icon': features['icon'],
                    'method': methods.get(best_type, '综合判断'),
                    'score': round(scores[best_type], 2)
                }
        
        return {
            'type': 'unknown',
            'type_cn': '未知材料',
            'confidence': 0.0,
            'tags': [],
            'icon': '📦',
            'method': '无法识别',
            'score': 0.0
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
    
    def find_similar_materials(self, material_type, limit=5):
        """查找相似材料"""
        from apps.materials.models import Material
        
        if material_type == 'unknown':
            return []
        
        type_cn = self.MATERIAL_PATTERNS.get(material_type, {}).get('name_cn', '')
        if not type_cn:
            return []
        
        # 查找同类型的材料
        materials = Material.objects.filter(
            tags__icontains=type_cn
        ).order_by('-created_at')[:limit]
        
        return [
            {
                'id': m.id,
                'name': m.name or m.file.filename,
                'tags': m.tags
            }
            for m in materials
        ]
