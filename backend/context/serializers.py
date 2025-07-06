from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import ContextEntry, ContextInsight, ContextProcessingLog


class ContextInsightSerializer(serializers.ModelSerializer):
    """Serializer for ContextInsight model"""
    
    class Meta:
        model = ContextInsight
        fields = [
            'id', 'insight_type', 'title', 'description', 'confidence_score',
            'metadata', 'is_actionable', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContextProcessingLogSerializer(serializers.ModelSerializer):
    """Serializer for ContextProcessingLog model"""
    
    class Meta:
        model = ContextProcessingLog
        fields = [
            'id', 'processing_step', 'status', 'details', 'processing_time',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContextEntryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for context entry list views"""
    content_preview = serializers.CharField(read_only=True)
    urgency_level = serializers.CharField(read_only=True)
    has_extracted_tasks = serializers.BooleanField(read_only=True)
    insights_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ContextEntry
        fields = [
            'id', 'title', 'source_type', 'sender', 'timestamp',
            'processing_status', 'relevance_score', 'content_preview',
            'urgency_level', 'has_extracted_tasks', 'insights_count',
            'created_at', 'updated_at'
        ]

    def get_insights_count(self, obj):
        """Get the count of insights for this context entry"""
        return obj.insights.count()


class ContextEntryDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual context entries"""
    urgency_level = serializers.CharField(read_only=True)
    has_extracted_tasks = serializers.BooleanField(read_only=True)
    insights = ContextInsightSerializer(many=True, read_only=True)
    processing_logs = ContextProcessingLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = ContextEntry
        fields = [
            'id', 'title', 'content', 'source_type', 'sender', 'recipients',
            'timestamp', 'processing_status', 'processed_insights',
            'extracted_tasks', 'priority_indicators', 'deadline_mentions',
            'key_entities', 'sentiment_analysis', 'categories', 'relevance_score',
            'processing_attempts', 'last_processed_at', 'processing_error',
            'urgency_level', 'has_extracted_tasks', 'insights', 'processing_logs',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'processing_status', 'processed_insights', 'extracted_tasks',
            'priority_indicators', 'deadline_mentions', 'key_entities',
            'sentiment_analysis', 'categories', 'relevance_score',
            'processing_attempts', 'last_processed_at', 'processing_error',
            'urgency_level', 'has_extracted_tasks', 'created_at', 'updated_at'
        ]


class ContextEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating context entries"""
    
    class Meta:
        model = ContextEntry
        fields = [
            'title', 'content', 'source_type', 'sender', 'recipients', 'timestamp'
        ]

    def validate_content(self, value):
        """Validate content is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value.strip()

    def validate_timestamp(self, value):
        """Validate timestamp is not in the future"""
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value

    def create(self, validated_data):
        """Create a new context entry with the authenticated user"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class ContextEntryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating context entries"""
    
    class Meta:
        model = ContextEntry
        fields = ['title', 'content', 'sender', 'recipients']

    def validate_content(self, value):
        """Validate content is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value.strip()


class ContextAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for context analysis requests"""
    context_entry_id = serializers.IntegerField()
    analysis_type = serializers.ChoiceField(
        choices=[
            ('full', 'Full Analysis'),
            ('tasks_only', 'Extract Tasks Only'),
            ('sentiment_only', 'Sentiment Analysis Only'),
            ('entities_only', 'Entity Extraction Only'),
        ],
        default='full'
    )
    force_reprocess = serializers.BooleanField(default=False)
    
    def validate_context_entry_id(self, value):
        """Validate that the context entry exists and belongs to the user"""
        user = self.context['request'].user
        try:
            context_entry = ContextEntry.objects.get(id=value, user=user)
        except ContextEntry.DoesNotExist:
            raise serializers.ValidationError("Context entry not found or access denied.")
        return value


class BulkContextAnalysisSerializer(serializers.Serializer):
    """Serializer for bulk context analysis requests"""
    context_entry_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    analysis_type = serializers.ChoiceField(
        choices=[
            ('full', 'Full Analysis'),
            ('tasks_only', 'Extract Tasks Only'),
            ('sentiment_only', 'Sentiment Analysis Only'),
        ],
        default='full'
    )
    force_reprocess = serializers.BooleanField(default=False)
    
    def validate_context_entry_ids(self, value):
        """Validate that all context entries exist and belong to the user"""
        user = self.context['request'].user
        entries = ContextEntry.objects.filter(id__in=value, user=user)
        if len(entries) != len(value):
            raise serializers.ValidationError("Some context entries not found or access denied.")
        return value


class ContextInsightCreateSerializer(serializers.ModelSerializer):
    """Serializer for manually creating context insights"""
    
    class Meta:
        model = ContextInsight
        fields = [
            'context_entry', 'insight_type', 'title', 'description',
            'confidence_score', 'metadata', 'is_actionable'
        ]

    def validate_confidence_score(self, value):
        """Validate confidence score is between 0 and 100"""
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Confidence score must be between 0 and 100.")
        return value

    def validate_context_entry(self, value):
        """Validate that the context entry belongs to the user"""
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("Access denied to this context entry.")
        return value


class ContextSummarySerializer(serializers.Serializer):
    """Serializer for context summary data"""
    total_entries = serializers.IntegerField()
    entries_by_source = serializers.DictField()
    pending_processing = serializers.IntegerField()
    high_relevance_entries = serializers.IntegerField()
    extracted_tasks_count = serializers.IntegerField()
    avg_relevance_score = serializers.FloatField()
    recent_activity = serializers.ListField()
    
    class Meta:
        fields = [
            'total_entries', 'entries_by_source', 'pending_processing',
            'high_relevance_entries', 'extracted_tasks_count',
            'avg_relevance_score', 'recent_activity'
        ]