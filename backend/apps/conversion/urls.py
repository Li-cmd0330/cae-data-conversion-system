from django.urls import path
from .views import convert_material

urlpatterns = [
    path('materials/<int:material_id>/', convert_material, name='convert-material'),
]
