from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContextEntryViewSet, ContextInsightViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'entries', ContextEntryViewSet, basename='contextentry')
router.register(r'insights', ContextInsightViewSet, basename='contextinsight')

app_name = 'context'

urlpatterns = [
    path('api/v1/', include(router.urls)),
]