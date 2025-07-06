from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from django.utils import timezone

from .models import Task, Category, TaskComment
from .serializers import (
    TaskListSerializer, TaskDetailSerializer, TaskCreateUpdateSerializer,
    CategorySerializer, TaskCommentSerializer, TaskAIAnalysisSerializer,
    TaskPrioritizationSerializer, TaskBulkUpdateSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing task categories"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'usage_frequency', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Return categories with usage frequency for the current user"""
        return Category.objects.all()


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tasks with AI integration"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['priority_score', 'deadline', 'created_at', 'updated_at']
    ordering = ['-priority_score', '-created_at']

    def get_queryset(self):
        """Return tasks for the authenticated user"""
        return Task.objects.filter(assigned_to=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        else:
            return TaskDetailSerializer

    def perform_create(self, serializer):
        """Create task with authenticated user as assigned_to"""
        serializer.save(assigned_to=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark a task as completed"""
        task = self.get_object()
        task.mark_completed()
        return Response({'status': 'Task marked as completed'})

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        overdue_tasks = self.get_queryset().filter(
            deadline__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        """Get high priority tasks (priority_score >= 70)"""
        high_priority_tasks = self.get_queryset().filter(priority_score__gte=70)
        serializer = self.get_serializer(high_priority_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get tasks grouped by status"""
        statuses = ['todo', 'in_progress', 'completed', 'cancelled']
        result = {}
        
        for status_choice in statuses:
            tasks = self.get_queryset().filter(status=status_choice)
            serializer = self.get_serializer(tasks, many=True)
            result[status_choice] = serializer.data
            
        return Response(result)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update multiple tasks"""
        serializer = TaskBulkUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task_ids = serializer.validated_data['task_ids']
            updates = serializer.validated_data['updates']
            
            # Validate that all tasks belong to the user
            tasks = self.get_queryset().filter(id__in=task_ids)
            if len(tasks) != len(task_ids):
                return Response(
                    {'error': 'Some tasks not found or access denied'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform bulk update
            updated_count = tasks.update(**updates)
            
            return Response({
                'message': f'Successfully updated {updated_count} tasks',
                'updated_tasks': task_ids
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def ai_analysis(self, request, pk=None):
        """Request AI analysis for a specific task"""
        task = self.get_object()
        serializer = TaskAIAnalysisSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Here we would call the AI service to analyze the task
            # For now, return a mock response
            analysis_result = {
                'task_id': task.id,
                'priority_analysis': {
                    'suggested_priority_score': 75.0,
                    'factors': [
                        'Deadline proximity',
                        'Task complexity',
                        'Dependencies'
                    ],
                    'confidence': 85.0
                },
                'deadline_suggestion': {
                    'suggested_deadline': '2024-12-30T10:00:00Z',
                    'reasoning': 'Based on task complexity and current workload',
                    'confidence': 80.0
                },
                'enhancement_suggestions': [
                    'Break down into smaller subtasks',
                    'Add specific deliverables',
                    'Set intermediate checkpoints'
                ]
            }
            
            return Response(analysis_result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def ai_prioritization(self, request):
        """Request AI prioritization for multiple tasks"""
        serializer = TaskPrioritizationSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            task_ids = serializer.validated_data['task_ids']
            tasks = self.get_queryset().filter(id__in=task_ids)
            
            # Mock AI prioritization response
            prioritization_result = {
                'prioritized_tasks': [
                    {
                        'task_id': task.id,
                        'current_priority_score': task.priority_score,
                        'suggested_priority_score': min(task.priority_score + 10, 100),
                        'ranking': idx + 1,
                        'reasoning': f'Task "{task.title}" requires immediate attention'
                    }
                    for idx, task in enumerate(tasks.order_by('-priority_score'))
                ],
                'analysis_summary': {
                    'total_tasks_analyzed': len(tasks),
                    'high_priority_count': len([t for t in tasks if t.priority_score >= 70]),
                    'recommendations': [
                        'Focus on overdue tasks first',
                        'Consider delegating lower priority items'
                    ]
                }
            }
            
            return Response(prioritization_result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics for tasks"""
        queryset = self.get_queryset()
        
        stats = {
            'total_tasks': queryset.count(),
            'completed_tasks': queryset.filter(status='completed').count(),
            'pending_tasks': queryset.filter(status__in=['todo', 'in_progress']).count(),
            'overdue_tasks': queryset.filter(
                deadline__lt=timezone.now(),
                status__in=['todo', 'in_progress']
            ).count(),
            'high_priority_tasks': queryset.filter(priority_score__gte=70).count(),
            'avg_priority_score': queryset.aggregate(
                avg_score=Avg('priority_score')
            )['avg_score'] or 0,
            'tasks_by_status': {
                status_choice[0]: queryset.filter(status=status_choice[0]).count()
                for status_choice in Task.STATUS_CHOICES
            },
            'tasks_by_priority': {
                priority[0]: queryset.filter(priority=priority[0]).count()
                for priority in Task.PRIORITY_CHOICES
            }
        }
        
        return Response(stats)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing task comments"""
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        """Return comments for tasks assigned to the user"""
        return TaskComment.objects.filter(task__assigned_to=self.request.user)

    def perform_create(self, serializer):
        """Create comment with authenticated user as author"""
        serializer.save(author=self.request.user)
