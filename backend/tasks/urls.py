from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet, TaskCommentViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'comments', TaskCommentViewSet, basename='taskcomment')

app_name = 'tasks'

urlpatterns = [
    path('api/v1/', include(router.urls)),
]