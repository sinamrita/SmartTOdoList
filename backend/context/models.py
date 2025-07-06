from django.db import models
from django.contrib.auth.models import User


class ContextEntry(models.Model):
    """Model for storing daily context data (messages, emails, notes)"""
    
    SOURCE_TYPES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('notes', 'Notes'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('calendar', 'Calendar'),
        ('manual', 'Manual Entry'),
        ('other', 'Other'),
    ]
    
    PROCESSING_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    # Basic information
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(help_text="Raw content of the context entry")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='context_entries')
    
    # Metadata
    sender = models.CharField(max_length=100, blank=True, help_text="Sender name or email")
    recipients = models.JSONField(default=list, help_text="List of recipients")
    timestamp = models.DateTimeField(help_text="When the context was created/received")
    
    # AI Processing fields
    processing_status = models.CharField(
        max_length=15,
        choices=PROCESSING_STATUS,
        default='pending'
    )
    processed_insights = models.JSONField(
        default=dict,
        help_text="AI-extracted insights from the content"
    )
    extracted_tasks = models.JSONField(
        default=list,
        help_text="Tasks identified from the context"
    )
    priority_indicators = models.JSONField(
        default=dict,
        help_text="Priority indicators extracted from context"
    )
    deadline_mentions = models.JSONField(
        default=list,
        help_text="Deadline mentions found in context"
    )
    key_entities = models.JSONField(
        default=list,
        help_text="Key entities (people, places, projects) mentioned"
    )
    sentiment_analysis = models.JSONField(
        default=dict,
        help_text="Sentiment analysis results"
    )
    
    # Context categorization
    categories = models.JSONField(
        default=list,
        help_text="AI-suggested categories for this context"
    )
    relevance_score = models.FloatField(
        default=0.0,
        help_text="Relevance score for task management (0-100)"
    )
    
    # Processing metadata
    processing_attempts = models.IntegerField(default=0)
    last_processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp', '-created_at']
        indexes = [
            models.Index(fields=['user', 'source_type']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['relevance_score']),
        ]
        verbose_name_plural = "Context Entries"

    def __str__(self):
        title = self.title or f"{self.source_type.title()} entry"
        return f"{title} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def mark_processing_complete(self, insights=None):
        """Mark context processing as complete"""
        self.processing_status = 'completed'
        self.last_processed_at = models.timezone.now()
        if insights:
            self.processed_insights = insights
        self.save()

    def mark_processing_failed(self, error_message):
        """Mark context processing as failed"""
        self.processing_status = 'failed'
        self.processing_error = error_message
        self.processing_attempts += 1
        self.save()

    @property
    def content_preview(self):
        """Return a preview of the content (first 100 characters)"""
        if len(self.content) > 100:
            return self.content[:100] + "..."
        return self.content

    @property
    def has_extracted_tasks(self):
        """Check if any tasks were extracted from this context"""
        return bool(self.extracted_tasks)

    @property
    def urgency_level(self):
        """Calculate urgency level based on content analysis"""
        if self.relevance_score >= 80:
            return 'high'
        elif self.relevance_score >= 50:
            return 'medium'
        else:
            return 'low'


class ContextProcessingLog(models.Model):
    """Model for logging context processing activities"""
    
    context_entry = models.ForeignKey(
        ContextEntry,
        on_delete=models.CASCADE,
        related_name='processing_logs'
    )
    processing_step = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    details = models.JSONField(default=dict)
    processing_time = models.FloatField(help_text="Processing time in seconds")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.processing_step} - {self.status}"


class ContextInsight(models.Model):
    """Model for storing specific insights extracted from context"""
    
    INSIGHT_TYPES = [
        ('task', 'Task Suggestion'),
        ('deadline', 'Deadline Mention'),
        ('priority', 'Priority Indicator'),
        ('contact', 'Contact Information'),
        ('meeting', 'Meeting Information'),
        ('project', 'Project Reference'),
        ('other', 'Other Insight'),
    ]

    context_entry = models.ForeignKey(
        ContextEntry,
        on_delete=models.CASCADE,
        related_name='insights'
    )
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.FloatField(
        help_text="AI confidence score (0-100)"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata for the insight"
    )
    is_actionable = models.BooleanField(
        default=False,
        help_text="Whether this insight requires action"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-confidence_score', '-created_at']

    def __str__(self):
        return f"{self.insight_type.title()}: {self.title}"
