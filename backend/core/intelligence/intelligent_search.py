"""
智能搜索推荐器
提供模糊搜索、相似材料推荐、个性化推荐
"""
from django.db.models import Q, Count
from difflib import SequenceMatcher


class IntelligentSearch:
    """智能搜索推荐器"""
    
    def fuzzy_search(self, query, limit=20):
        """
        模糊搜索材料
        
        Args:
            query: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            [
                {
                    'material': Material对象,
                    'score': 相似度分数,
                    'match_field': 匹配字段
                }
            ]
        """
        from apps.materials.models import Material
        
        if not query:
            return []
        
        query_upper = query.upper()
        results = []
        
        # 1. 精确匹配（最高优先级）
        exact_matches = Material.objects.filter(
            Q(name__iexact=query) | 
            Q(file__filename__iexact=query)
        )
        for mat in exact_matches:
            results.append({
                'material': mat,
                'score': 1.0,
                'match_field': 'exact',
                'match_reason': '精确匹配'
            })
        
        # 2. 包含匹配
        contains_matches = Material.objects.filter(
            Q(name__icontains=query) | 
            Q(file__filename__icontains=query) |
            Q(tags__icontains=query) |
            Q(notes__icontains=query)
        ).exclude(
            id__in=[r['material'].id for r in results]
        )
        
        for mat in contains_matches:
            score = 0.8
            match_field = 'contains'
            match_reason = '部分匹配'
            
            # 提高匹配度
            if mat.name and query_upper in mat.name.upper():
                score = 0.9
                match_field = 'name'
                match_reason = '名称匹配'
            elif mat.file and query_upper in mat.file.filename.upper():
                score = 0.85
                match_field = 'filename'
                match_reason = '文件名匹配'
            elif mat.tags and query_upper in mat.tags.upper():
                score = 0.75
                match_field = 'tags'
                match_reason = '标签匹配'
            
            results.append({
                'material': mat,
                'score': score,
                'match_field': match_field,
                'match_reason': match_reason
            })
        
        # 3. 相似度匹配（使用编辑距离）
        if len(results) < limit:
            all_materials = Material.objects.exclude(
                id__in=[r['material'].id for r in results]
            )[:100]  # 限制范围避免性能问题
            
            for mat in all_materials:
                # 计算与名称的相似度
                name_similarity = self._calculate_similarity(
                    query, 
                    mat.name or mat.file.filename
                )
                
                # 计算与标签的相似度
                tag_similarity = 0
                if mat.tags:
                    for tag in mat.tags.split(','):
                        tag_sim = self._calculate_similarity(query, tag.strip())
                        tag_similarity = max(tag_similarity, tag_sim)
                
                # 取最高相似度
                similarity = max(name_similarity, tag_similarity)
                
                if similarity > 0.5:  # 相似度阈值
                    results.append({
                        'material': mat,
                        'score': similarity * 0.7,  # 降低权重
                        'match_field': 'similarity',
                        'match_reason': f'相似度匹配 ({int(similarity * 100)}%)'
                    })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:limit]
    
    def recommend_similar(self, material_id, limit=5):
        """
        推荐相似材料
        
        Args:
            material_id: 材料ID
            limit: 推荐数量
            
        Returns:
            [
                {
                    'material': Material对象,
                    'similarity': 相似度,
                    'reason': 推荐理由
                }
            ]
        """
        from apps.materials.models import Material
        
        try:
            source_material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            return []
        
        recommendations = []
        
        # 1. 基于标签推荐
        if source_material.tags:
            tags = [t.strip() for t in source_material.tags.split(',') if t.strip()]
            if tags:
                tag_matches = Material.objects.filter(
                    tags__icontains=tags[0]
                ).exclude(id=material_id)[:limit * 2]
                
                for mat in tag_matches:
                    # 计算标签重叠度
                    mat_tags = [t.strip() for t in (mat.tags or '').split(',') if t.strip()]
                    common_tags = set(tags) & set(mat_tags)
                    similarity = len(common_tags) / max(len(tags), len(mat_tags)) if tags or mat_tags else 0
                    
                    if similarity > 0:
                        recommendations.append({
                            'material': mat,
                            'similarity': similarity,
                            'reason': f'相同标签: {", ".join(common_tags)}',
                            'score': similarity * 1.0
                        })
        
        # 2. 基于参数相似度推荐
        source_data = source_material.normalized_data or source_material.raw_data
        if source_data:
            source_young = self._extract_numeric(source_data.get('YOUNG'))
            source_masden = self._extract_numeric(source_data.get('MASDEN'))
            
            if source_young or source_masden:
                all_materials = Material.objects.exclude(
                    id__in=[material_id] + [r['material'].id for r in recommendations]
                )[:50]
                
                for mat in all_materials:
                    mat_data = mat.normalized_data or mat.raw_data
                    if not mat_data:
                        continue
                    
                    mat_young = self._extract_numeric(mat_data.get('YOUNG'))
                    mat_masden = self._extract_numeric(mat_data.get('MASDEN'))
                    
                    # 计算参数相似度
                    similarity_score = 0
                    reasons = []
                    
                    if source_young and mat_young:
                        young_diff = abs(source_young - mat_young) / source_young
                        if young_diff < 0.2:  # 20%以内
                            similarity_score += 0.5
                            reasons.append('杨氏模量相近')
                    
                    if source_masden and mat_masden:
                        masden_diff = abs(source_masden - mat_masden) / source_masden
                        if masden_diff < 0.2:  # 20%以内
                            similarity_score += 0.5
                            reasons.append('密度相近')
                    
                    if similarity_score > 0:
                        recommendations.append({
                            'material': mat,
                            'similarity': similarity_score,
                            'reason': ', '.join(reasons),
                            'score': similarity_score * 0.8
                        })
        
        # 3. 基于文件名相似度推荐
        source_filename = source_material.file.filename if source_material.file else ''
        if source_filename:
            # 提取材料代号（如AL6061）
            material_code = self._extract_material_code(source_filename)
            if material_code:
                code_matches = Material.objects.filter(
                    file__filename__icontains=material_code
                ).exclude(
                    id__in=[material_id] + [r['material'].id for r in recommendations]
                )[:limit]
                
                for mat in code_matches:
                    recommendations.append({
                        'material': mat,
                        'similarity': 0.7,
                        'reason': f'相同材料系列: {material_code}',
                        'score': 0.7
                    })
        
        # 按分数排序并去重
        seen_ids = set()
        unique_recommendations = []
        for rec in sorted(recommendations, key=lambda x: x['score'], reverse=True):
            if rec['material'].id not in seen_ids:
                seen_ids.add(rec['material'].id)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:limit]
    
    def get_popular_materials(self, limit=10):
        """
        获取热门材料（基于收藏和使用频率）
        
        Args:
            limit: 返回数量
            
        Returns:
            [Material对象列表]
        """
        from apps.materials.models import Material
        
        # 优先返回收藏的材料
        favorites = Material.objects.filter(is_favorite=True).order_by('-created_at')[:limit]
        
        if favorites.count() >= limit:
            return list(favorites)
        
        # 补充最近上传的材料
        recent = Material.objects.order_by('-created_at')[:limit]
        
        return list(recent)
    
    def get_recommendations_by_tags(self, tags, limit=5):
        """
        基于标签推荐材料
        
        Args:
            tags: 标签列表
            limit: 推荐数量
            
        Returns:
            [Material对象列表]
        """
        from apps.materials.models import Material
        
        if not tags:
            return []
        
        # 查找包含任一标签的材料
        query = Q()
        for tag in tags:
            query |= Q(tags__icontains=tag)
        
        materials = Material.objects.filter(query).order_by('-created_at')[:limit]
        
        return list(materials)
    
    def _calculate_similarity(self, str1, str2):
        """计算两个字符串的相似度（0-1）"""
        if not str1 or not str2:
            return 0.0
        
        return SequenceMatcher(None, str1.upper(), str2.upper()).ratio()
    
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
    
    def _extract_material_code(self, filename):
        """从文件名提取材料代号"""
        import re
        
        # 常见材料代号模式
        patterns = [
            r'(AL\d{4})',  # AL6061
            r'(AISI[-\s]?\d{4})',  # AISI-1015
            r'(INCONEL[-\s]?\d{3})',  # INCONEL-625
            r'(TI[-\s]?TYPE[-\s]?\d+)',  # TI-TYPE-1
            r'(C\d{5})',  # C10100
        ]
        
        filename_upper = filename.upper()
        for pattern in patterns:
            match = re.search(pattern, filename_upper)
            if match:
                return match.group(1)
        
        return None
