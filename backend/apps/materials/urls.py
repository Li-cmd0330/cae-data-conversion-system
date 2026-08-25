from rest_framework.routers import DefaultRouter
from .views import ExportRecordViewSet, MaterialViewSet

router = DefaultRouter()
router.register('', MaterialViewSet, basename='material')
router.register('exports', ExportRecordViewSet, basename='material-export')

urlpatterns = router.urls
