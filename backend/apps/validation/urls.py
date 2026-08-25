from django.urls import path
from .views import validate_material

urlpatterns = [
    path('materials/<int:material_id>/', validate_material, name='validate-material'),
]
