# Generated by Django 4.2.7 on 2025-07-06 14:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('api_endpoint', models.URLField()),
                ('is_active', models.BooleanField(default=True)),
                ('supports_context_analysis', models.BooleanField(default=True)),
                ('supports_task_prioritization', models.BooleanField(default=True)),
                ('supports_deadline_suggestion', models.BooleanField(default=True)),
                ('rate_limit_per_minute', models.IntegerField(default=60)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserAIPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_prioritize_tasks', models.BooleanField(default=True)),
                ('auto_suggest_deadlines', models.BooleanField(default=True)),
                ('auto_categorize_tasks', models.BooleanField(default=True)),
                ('auto_process_context', models.BooleanField(default=True)),
                ('notify_ai_suggestions', models.BooleanField(default=True)),
                ('notify_context_insights', models.BooleanField(default=True)),
                ('notify_deadline_recommendations', models.BooleanField(default=True)),
                ('minimum_confidence_threshold', models.FloatField(default=70.0)),
                ('enable_fallback_providers', models.BooleanField(default=True)),
                ('allow_content_analysis', models.BooleanField(default=True)),
                ('store_ai_interactions', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('preferred_provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ai_integration.aiprovider')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ai_preferences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TaskAIAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority_analysis', models.JSONField(default=dict, help_text='AI analysis of task priority factors')),
                ('complexity_assessment', models.JSONField(default=dict, help_text='Assessment of task complexity')),
                ('deadline_recommendation', models.JSONField(default=dict, help_text='AI recommendation for deadline')),
                ('category_suggestions', models.JSONField(default=list, help_text='AI-suggested categories')),
                ('dependency_analysis', models.JSONField(default=dict, help_text='Analysis of task dependencies')),
                ('risk_assessment', models.JSONField(default=dict, help_text='Risk factors and mitigation suggestions')),
                ('analysis_confidence', models.FloatField(default=0.0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('analysis_version', models.CharField(default='1.0', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ai_analysis', to='tasks.task')),
            ],
        ),
        migrations.CreateModel(
            name='AIRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(choices=[('context_analysis', 'Context Analysis'), ('task_prioritization', 'Task Prioritization'), ('deadline_suggestion', 'Deadline Suggestion'), ('task_enhancement', 'Task Enhancement'), ('categorization', 'Categorization'), ('sentiment_analysis', 'Sentiment Analysis'), ('entity_extraction', 'Entity Extraction')], max_length=30)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('timeout', 'Timeout')], default='pending', max_length=15)),
                ('input_data', models.JSONField(help_text='Input data sent to AI')),
                ('prompt_template', models.TextField(blank=True)),
                ('model_name', models.CharField(blank=True, max_length=100)),
                ('response_data', models.JSONField(blank=True, help_text='Response from AI', null=True)),
                ('confidence_score', models.FloatField(blank=True, null=True)),
                ('processing_time', models.FloatField(blank=True, help_text='Processing time in seconds', null=True)),
                ('token_usage', models.JSONField(blank=True, help_text='Token usage statistics', null=True)),
                ('cost_estimate', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('retry_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ai_integration.aiprovider')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'request_type'], name='ai_integrat_user_id_6c06eb_idx'), models.Index(fields=['status'], name='ai_integrat_status_ad5fd5_idx'), models.Index(fields=['provider', 'created_at'], name='ai_integrat_provide_82450c_idx')],
            },
        ),
        migrations.CreateModel(
            name='AIModelPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=100)),
                ('request_type', models.CharField(max_length=30)),
                ('total_requests', models.IntegerField(default=0)),
                ('successful_requests', models.IntegerField(default=0)),
                ('failed_requests', models.IntegerField(default=0)),
                ('average_processing_time', models.FloatField(default=0.0)),
                ('average_confidence_score', models.FloatField(default=0.0)),
                ('total_cost', models.DecimalField(decimal_places=4, default=0.0, max_digits=10)),
                ('total_tokens_used', models.BigIntegerField(default=0)),
                ('user_satisfaction_score', models.FloatField(default=0.0, help_text='Average user rating')),
                ('accuracy_score', models.FloatField(default=0.0, help_text='Model accuracy assessment')),
                ('date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ai_integration.aiprovider')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('provider', 'model_name', 'request_type', 'date')},
            },
        ),
    ]
