from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.visualization.chart_data_builder import ChartDataBuilder
from .models import ExportRecord, Material
from .serializers import (
    ExportRecordSerializer,
    MaterialBatchExportSerializer,
    MaterialSerializer,
    MaterialUpdateSerializer,
    MaterialUploadSerializer,
    ValidationReportSerializer,
)
from .services import ExportService, MaterialService


def extract_numeric_value(field_data):
    """从字段数据中提取数值"""
    if field_data is None:
        return None
    if isinstance(field_data, (int, float)):
        return round(field_data, 6)
    if isinstance(field_data, dict):
        if 'value' in field_data:
            val = field_data['value']
            return round(val, 6) if isinstance(val, (int, float)) else val
        if 'values' in field_data and field_data['values']:
            first = field_data['values'][0]
            return round(first, 6) if isinstance(first, (int, float)) else first
    if isinstance(field_data, list) and field_data:
        first = field_data[0]
        return round(first, 6) if isinstance(first, (int, float)) else first
    return str(field_data)[:50] if field_data else None


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.select_related('file').all().order_by('-created_at')
    serializer_class = MaterialSerializer

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return MaterialUpdateSerializer
        return MaterialSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        tags = self.request.query_params.get('tags')
        is_favorite = self.request.query_params.get('is_favorite')
        has_fstres = self.request.query_params.get('has_fstres')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(file__filename__icontains=search) | Q(notes__icontains=search)
            )
        if tags:
            queryset = queryset.filter(tags__icontains=tags)
        if is_favorite == 'true':
            queryset = queryset.filter(is_favorite=True)
        if has_fstres == 'true':
            queryset = queryset.filter(
                Q(normalized_data__FSTRES__isnull=False) | Q(raw_data__FSTRES__isnull=False)
            )
        
        return queryset

    def _build_upload_response(self, material, validation):
        return {
            'material_id': material.id,
            'filename': material.file.filename,
            'material_name': material.name,
            'unit_system': material.unit_system,
            'parsed_data': material.normalized_data,
            'source_file_retained': bool(material.file.original_file),
            'validation': ValidationReportSerializer(validation).data,
        }

    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        serializer = MaterialUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = MaterialService.parse_uploaded_file(serializer.validated_data['file'])
        return Response(
            self._build_upload_response(result['material'], result['validation']),
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'], url_path='batch-upload')
    def batch_upload(self, request):
        files = request.FILES.getlist('files') or request.FILES.getlist('file')
        if not files:
            return Response({'detail': '请至少上传一个 KEY 文件'}, status=status.HTTP_400_BAD_REQUEST)
        results = MaterialService.parse_uploaded_files(files)
        payload = [self._build_upload_response(item['material'], item['validation']) for item in results]
        return Response({'count': len(payload), 'results': payload}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='clear-history')
    def clear_history(self, request):
        material_count = Material.objects.count()
        export_count = ExportRecord.objects.count()
        for record in ExportRecord.objects.exclude(file=''):
            if record.file:
                record.file.delete(save=False)
        Material.objects.all().delete()
        return Response({'deleted_materials': material_count, 'deleted_exports': export_count})

    @action(detail=True, methods=['post'], url_path='validate')
    def validate(self, request, pk=None):
        material = self.get_object()
        report = MaterialService.validate_material(material)
        return Response(ValidationReportSerializer(report).data)

    @action(detail=True, methods=['post'], url_path='convert')
    def convert(self, request, pk=None):
        material = self.get_object()
        target_format = request.data.get('target_format', 'json')
        record = ExportService.export_material(material, target_format)
        return Response(ExportRecordSerializer(record, context={'request': request}).data)

    @action(detail=False, methods=['post'], url_path='batch-convert')
    def batch_convert(self, request):
        serializer = MaterialBatchExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        records = ExportService.export_materials(
            serializer.validated_data['material_ids'],
            serializer.validated_data['target_format'],
        )
        return Response({
            'count': len(records),
            'results': ExportRecordSerializer(records, many=True, context={'request': request}).data,
        })

    @action(detail=False, methods=['post'], url_path='compare')
    def compare(self, request):
        material_ids = request.data.get('material_ids', [])
        if len(material_ids) < 2:
            return Response({'detail': '至少选择2个材料进行对比'}, status=status.HTTP_400_BAD_REQUEST)
        
        materials = Material.objects.filter(id__in=material_ids).select_related('file')
        comparison = []
        for mat in materials:
            data = mat.normalized_data or mat.raw_data
            comparison.append({
                'id': mat.id,
                'name': mat.name,
                'filename': mat.file.filename,
                'unit_system': mat.unit_system,
                'young': extract_numeric_value(data.get('YOUNG')),
                'poison': extract_numeric_value(data.get('POISON')),
                'masden': extract_numeric_value(data.get('MASDEN')),
                'thrcnd': extract_numeric_value(data.get('THRCND')),
                'heatcp': extract_numeric_value(data.get('HEATCP')),
                'expand': extract_numeric_value(data.get('EXPAND')),
                'has_fstres': bool(data.get('FSTRES')),
                'tags': mat.tags,
                'is_favorite': mat.is_favorite,
            })
        return Response({'materials': comparison})

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        from django.db.models import Count
        total_materials = Material.objects.count()
        total_exports = ExportRecord.objects.count()
        successful_exports = ExportRecord.objects.filter(status='success').count()
        favorite_materials = Material.objects.filter(is_favorite=True).count()
        materials_with_fstres = Material.objects.filter(
            Q(normalized_data__FSTRES__isnull=False) | Q(raw_data__FSTRES__isnull=False)
        ).count()
        export_by_format = ExportRecord.objects.values('target_format').annotate(count=Count('id'))
        recent_materials = Material.objects.order_by('-created_at')[:5].values('id', 'name', 'file__filename', 'created_at', 'is_favorite')
        
        all_tags = []
        for mat in Material.objects.exclude(tags=''):
            all_tags.extend([t.strip() for t in mat.tags.split(',') if t.strip()])
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return Response({
            'total_materials': total_materials,
            'total_exports': total_exports,
            'successful_exports': successful_exports,
            'favorite_materials': favorite_materials,
            'materials_with_fstres': materials_with_fstres,
            'export_by_format': list(export_by_format),
            'recent_materials': list(recent_materials),
            'popular_tags': popular_tags,
        })

    @action(detail=True, methods=['post'], url_path='toggle-favorite')
    def toggle_favorite(self, request, pk=None):
        material = self.get_object()
        material.is_favorite = not material.is_favorite
        material.save(update_fields=['is_favorite'])
        return Response({'is_favorite': material.is_favorite})

    @action(detail=True, methods=['get'], url_path='charts/flow-stress')
    def flow_stress_chart(self, request, pk=None):
        material = self.get_object()
        return Response(ChartDataBuilder().build_flow_stress_chart(material.normalized_data or material.raw_data))

    @action(detail=True, methods=['get'], url_path='charts/completeness')
    def completeness_chart(self, request, pk=None):
        material = self.get_object()
        return Response(ChartDataBuilder().build_completeness_radar(material.normalized_data or material.raw_data))
    
    @action(detail=False, methods=['get'], url_path='intelligent-search')
    def intelligent_search(self, request):
        """智能搜索"""
        from core.intelligence.intelligent_search import IntelligentSearch
        
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 20))
        
        search_engine = IntelligentSearch()
        results = search_engine.fuzzy_search(query, limit)
        
        return Response({
            'query': query,
            'count': len(results),
            'results': [
                {
                    'id': r['material'].id,
                    'name': r['material'].name or r['material'].file.filename,
                    'filename': r['material'].file.filename,
                    'tags': r['material'].tags,
                    'score': r['score'],
                    'match_reason': r['match_reason']
                }
                for r in results
            ]
        })
    
    @action(detail=True, methods=['get'], url_path='recommend-similar')
    def recommend_similar(self, request, pk=None):
        """推荐相似材料"""
        from core.intelligence.intelligent_search import IntelligentSearch
        
        limit = int(request.query_params.get('limit', 5))
        
        search_engine = IntelligentSearch()
        recommendations = search_engine.recommend_similar(pk, limit)
        
        return Response({
            'material_id': pk,
            'count': len(recommendations),
            'recommendations': [
                {
                    'id': r['material'].id,
                    'name': r['material'].name or r['material'].file.filename,
                    'filename': r['material'].file.filename,
                    'tags': r['material'].tags,
                    'similarity': r['similarity'],
                    'reason': r['reason']
                }
                for r in recommendations
            ]
        })
    
    @action(detail=False, methods=['get'], url_path='popular')
    def popular_materials(self, request):
        """获取热门材料"""
        from core.intelligence.intelligent_search import IntelligentSearch
        
        limit = int(request.query_params.get('limit', 10))
        
        search_engine = IntelligentSearch()
        materials = search_engine.get_popular_materials(limit)
        
        return Response({
            'count': len(materials),
            'materials': MaterialSerializer(materials, many=True).data
        })


class ExportRecordViewSet(viewsets.ModelViewSet):
    queryset = ExportRecord.objects.select_related('material').all().order_by('-created_at')
    serializer_class = ExportRecordSerializer
    http_method_names = ['get', 'delete', 'head', 'options']
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.file:
            instance.file.delete(save=False)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
