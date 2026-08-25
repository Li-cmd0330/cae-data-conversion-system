from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.materials.models import Material
from apps.materials.serializers import ExportRecordSerializer
from apps.materials.services import ExportService


@api_view(['POST'])
def convert_material(request, material_id):
    material = Material.objects.get(pk=material_id)
    record = ExportService.export_material(material, request.data.get('target_format', 'json'))
    return Response(ExportRecordSerializer(record, context={'request': request}).data)
