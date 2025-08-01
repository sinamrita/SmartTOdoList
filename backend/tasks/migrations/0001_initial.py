# Generated by Django 4.2.7 on 2025-07-06 14:10

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('color', models.CharField(default='#3B82F6', max_length=7)),
                ('description', models.TextField(blank=True)),
                ('usage_frequency', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='todo', max_length=15)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('priority_score', models.FloatField(default=50.0, help_text='AI-generated priority score (0-100)', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('ai_suggested_deadline', models.DateTimeField(blank=True, help_text='AI-suggested deadline based on task complexity and workload', null=True)),
                ('ai_enhanced_description', models.TextField(blank=True, help_text='AI-enhanced description with context-aware details')),
                ('ai_suggested_tags', models.JSONField(default=list, help_text='AI-suggested tags and categories')),
                ('context_insights', models.JSONField(default=dict, help_text='Insights extracted from daily context')),
                ('estimated_duration', models.IntegerField(blank=True, help_text='Estimated duration in minutes', null=True)),
                ('actual_duration', models.IntegerField(blank=True, help_text='Actual time taken in minutes', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tasks.category')),
            ],
            options={
                'ordering': ['-priority_score', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TaskComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('is_ai_generated', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tasks.task')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['status', 'priority_score'], name='tasks_task_status_60d34d_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['assigned_to', 'status'], name='tasks_task_assigne_b3b2bc_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['deadline'], name='tasks_task_deadlin_736196_idx'),
        ),
    ]
