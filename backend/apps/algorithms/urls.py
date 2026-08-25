from django.urls import path
from . import views

urlpatterns = [
    path('interpolate/', views.interpolate, name='interpolate'),
    path('flow-stress/predict/', views.flow_stress_predict, name='flow-stress-predict'),
    path('unit-convert/', views.unit_convert, name='unit-convert'),
    path('flow-stress/normalize/', views.normalize_fstres, name='normalize-fstres'),
    path('completeness/', views.material_completeness, name='material-completeness'),
    path('johnson-cook/value/', views.johnson_cook_value, name='johnson-cook-value'),
    path('johnson-cook/fit/', views.johnson_cook_fit, name='johnson-cook-fit'),
]
