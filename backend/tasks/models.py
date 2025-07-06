from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Model for task categories and tags"""
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color code
    description = models.TextField(blank=True)
    usage_frequency = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Task(models.Model):
    """Model for individual tasks with AI-powered features"""
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Basic task information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # AI-generated priority score (0-100)
    priority_score = models.FloatField(
        default=50.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="AI-generated priority score (0-100)"
    )
    
    # Dates and deadlines
    deadline = models.DateTimeField(null=True, blank=True)
    ai_suggested_deadline = models.DateTimeField(
        null=True, blank=True,
        help_text="AI-suggested deadline based on task complexity and workload"
    )
    
    # Relationships
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
    # AI enhancement fields
    ai_enhanced_description = models.TextField(
        blank=True,
        help_text="AI-enhanced description with context-aware details"
    )
    ai_suggested_tags = models.JSONField(
        default=list,
        help_text="AI-suggested tags and categories"
    )
    context_insights = models.JSONField(
        default=dict,
        help_text="Insights extracted from daily context"
    )
    
    # Metadata
    estimated_duration = models.IntegerField(
        null=True, blank=True,
        help_text="Estimated duration in minutes"
    )
    actual_duration = models.IntegerField(
        null=True, blank=True,
        help_text="Actual time taken in minutes"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority_score', '-created_at']
        indexes = [
            models.Index(fields=['status', 'priority_score']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return self.title

    def mark_completed(self):
        """Mark task as completed and set completion timestamp"""
        self.status = 'completed'
        self.completed_at = models.timezone.now()
        self.save()

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.deadline and self.status not in ['completed', 'cancelled']:
            return self.deadline < models.timezone.now()
        return False

    @property
    def urgency_level(self):
        """Calculate urgency level based on deadline and priority score"""
        if self.is_overdue:
            return 'overdue'
        elif self.priority_score >= 80:
            return 'critical'
        elif self.priority_score >= 60:
            return 'high'
        elif self.priority_score >= 40:
            return 'medium'
        else:
            return 'low'


class TaskComment(models.Model):
    """Model for task comments and updates"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on {self.task.title} by {self.author.username}"
