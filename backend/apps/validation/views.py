from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.materials.models import Material
from apps.materials.serializers import ValidationReportSerializer
from apps.materials.services import MaterialService


@api_view(['POST'])
def validate_material(request, material_id):
    material = Material.objects.get(pk=material_id)
    report = MaterialService.validate_material(material)
    return Response(ValidationReportSerializer(report).data)
