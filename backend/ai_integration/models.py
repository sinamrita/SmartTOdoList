from django.db import models
from django.contrib.auth.models import User


class AIProvider(models.Model):
    """Model for AI service providers"""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    api_endpoint = models.URLField()
    is_active = models.BooleanField(default=True)
    supports_context_analysis = models.BooleanField(default=True)
    supports_task_prioritization = models.BooleanField(default=True)
    supports_deadline_suggestion = models.BooleanField(default=True)
    rate_limit_per_minute = models.IntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AIRequest(models.Model):
    """Model for tracking AI API requests"""
    
    REQUEST_TYPES = [
        ('context_analysis', 'Context Analysis'),
        ('task_prioritization', 'Task Prioritization'),
        ('deadline_suggestion', 'Deadline Suggestion'),
        ('task_enhancement', 'Task Enhancement'),
        ('categorization', 'Categorization'),
        ('sentiment_analysis', 'Sentiment Analysis'),
        ('entity_extraction', 'Entity Extraction'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_requests')
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Request data
    input_data = models.JSONField(help_text="Input data sent to AI")
    prompt_template = models.TextField(blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    
    # Response data
    response_data = models.JSONField(null=True, blank=True, help_text="Response from AI")
    confidence_score = models.FloatField(null=True, blank=True)
    
    # Performance metrics
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in seconds")
    token_usage = models.JSONField(null=True, blank=True, help_text="Token usage statistics")
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'request_type']),
            models.Index(fields=['status']),
            models.Index(fields=['provider', 'created_at']),
        ]

    def __str__(self):
        return f"{self.request_type} - {self.status}"

    def mark_completed(self, response_data, processing_time=None):
        """Mark the request as completed with response data"""
        self.status = 'completed'
        self.response_data = response_data
        self.completed_at = models.timezone.now()
        if processing_time:
            self.processing_time = processing_time
        self.save()

    def mark_failed(self, error_message):
        """Mark the request as failed with error message"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = models.timezone.now()
        self.save()


class AIModelPerformance(models.Model):
    """Model for tracking AI model performance metrics"""
    
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    request_type = models.CharField(max_length=30)
    
    # Performance metrics
    total_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    average_processing_time = models.FloatField(default=0.0)
    average_confidence_score = models.FloatField(default=0.0)
    
    # Cost metrics
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    total_tokens_used = models.BigIntegerField(default=0)
    
    # Quality metrics
    user_satisfaction_score = models.FloatField(default=0.0, help_text="Average user rating")
    accuracy_score = models.FloatField(default=0.0, help_text="Model accuracy assessment")
    
    # Time period
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['provider', 'model_name', 'request_type', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.provider.name} - {self.model_name} - {self.date}"

    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


class TaskAIAnalysis(models.Model):
    """Model for storing AI analysis results for tasks"""
    
    task = models.OneToOneField(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='ai_analysis'
    )
    
    # Analysis results
    priority_analysis = models.JSONField(
        default=dict,
        help_text="AI analysis of task priority factors"
    )
    complexity_assessment = models.JSONField(
        default=dict,
        help_text="Assessment of task complexity"
    )
    deadline_recommendation = models.JSONField(
        default=dict,
        help_text="AI recommendation for deadline"
    )
    category_suggestions = models.JSONField(
        default=list,
        help_text="AI-suggested categories"
    )
    dependency_analysis = models.JSONField(
        default=dict,
        help_text="Analysis of task dependencies"
    )
    risk_assessment = models.JSONField(
        default=dict,
        help_text="Risk factors and mitigation suggestions"
    )
    
    # Quality metrics
    analysis_confidence = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    analysis_version = models.CharField(max_length=20, default='1.0')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Analysis for {self.task.title}"


class UserAIPreferences(models.Model):
    """Model for user AI preferences and settings"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_preferences')
    
    # Provider preferences
    preferred_provider = models.ForeignKey(
        AIProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # AI feature settings
    auto_prioritize_tasks = models.BooleanField(default=True)
    auto_suggest_deadlines = models.BooleanField(default=True)
    auto_categorize_tasks = models.BooleanField(default=True)
    auto_process_context = models.BooleanField(default=True)
    
    # Notification preferences
    notify_ai_suggestions = models.BooleanField(default=True)
    notify_context_insights = models.BooleanField(default=True)
    notify_deadline_recommendations = models.BooleanField(default=True)
    
    # Quality settings
    minimum_confidence_threshold = models.FloatField(default=70.0)
    enable_fallback_providers = models.BooleanField(default=True)
    
    # Privacy settings
    allow_content_analysis = models.BooleanField(default=True)
    store_ai_interactions = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI Preferences for {self.user.username}"
