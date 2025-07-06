from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Task, Category, TaskComment


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'color', 'description', 'usage_frequency',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_frequency', 'created_at', 'updated_at']


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for TaskComment model"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = [
            'id', 'content', 'author', 'author_name', 'is_ai_generated',
            'created_at'
        ]
        read_only_fields = ['id', 'author', 'created_at']


class TaskListSerializer(serializers.ModelSerializer):
    """Simplified serializer for task list views"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    urgency_level = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority', 'priority_score',
            'deadline', 'category', 'category_name', 'assigned_to',
            'assigned_to_name', 'urgency_level', 'is_overdue',
            'created_at', 'updated_at'
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual tasks"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    urgency_level = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'priority_score',
            'deadline', 'ai_suggested_deadline', 'category', 'category_name',
            'assigned_to', 'assigned_to_name', 'ai_enhanced_description',
            'ai_suggested_tags', 'context_insights', 'estimated_duration',
            'actual_duration', 'urgency_level', 'is_overdue', 'comments',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'priority_score', 'ai_suggested_deadline', 'ai_enhanced_description',
            'ai_suggested_tags', 'context_insights', 'urgency_level', 'is_overdue',
            'created_at', 'updated_at', 'completed_at'
        ]

    def validate_deadline(self, value):
        """Validate that deadline is in the future"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return value


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating tasks"""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'priority', 'deadline',
            'category', 'estimated_duration', 'actual_duration'
        ]

    def validate_title(self, value):
        """Validate task title"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()

    def create(self, validated_data):
        """Create a new task with the authenticated user as assigned_to"""
        user = self.context['request'].user
        validated_data['assigned_to'] = user
        return super().create(validated_data)


class TaskAIAnalysisSerializer(serializers.Serializer):
    """Serializer for AI analysis requests"""
    task_id = serializers.IntegerField()
    context_data = serializers.JSONField(required=False)
    user_preferences = serializers.JSONField(required=False)
    current_task_load = serializers.JSONField(required=False)
    
    def validate_task_id(self, value):
        """Validate that the task exists and belongs to the user"""
        user = self.context['request'].user
        try:
            task = Task.objects.get(id=value, assigned_to=user)
        except Task.DoesNotExist:
            raise serializers.ValidationError("Task not found or access denied.")
        return value


class TaskPrioritizationSerializer(serializers.Serializer):
    """Serializer for task prioritization requests"""
    task_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    context_data = serializers.JSONField(required=False)
    user_preferences = serializers.JSONField(required=False)
    
    def validate_task_ids(self, value):
        """Validate that all tasks exist and belong to the user"""
        user = self.context['request'].user
        tasks = Task.objects.filter(id__in=value, assigned_to=user)
        if len(tasks) != len(value):
            raise serializers.ValidationError("Some tasks not found or access denied.")
        return value


class TaskBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk task updates"""
    task_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    updates = serializers.DictField(allow_empty=False)
    
    def validate_updates(self, value):
        """Validate allowed fields for bulk update"""
        allowed_fields = ['status', 'priority', 'category', 'deadline']
        invalid_fields = set(value.keys()) - set(allowed_fields)
        if invalid_fields:
            raise serializers.ValidationError(
                f"Invalid fields for bulk update: {', '.join(invalid_fields)}"
            )
        return value