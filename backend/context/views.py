from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone

from .models import ContextEntry, ContextInsight, ContextProcessingLog
from .serializers import (
    ContextEntryListSerializer, ContextEntryDetailSerializer,
    ContextEntryCreateSerializer, ContextEntryUpdateSerializer,
    ContextInsightSerializer, ContextAnalysisRequestSerializer,
    BulkContextAnalysisSerializer, ContextSummarySerializer
)


class ContextEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing context entries"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source_type', 'processing_status']
    search_fields = ['title', 'content', 'sender']
    ordering_fields = ['timestamp', 'relevance_score', 'created_at']
    ordering = ['-timestamp', '-created_at']

    def get_queryset(self):
        """Return context entries for the authenticated user"""
        return ContextEntry.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ContextEntryListSerializer
        elif self.action == 'create':
            return ContextEntryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ContextEntryUpdateSerializer
        else:
            return ContextEntryDetailSerializer

    @action(detail=False, methods=['get'])
    def pending_processing(self, request):
        """Get context entries pending processing"""
        pending_entries = self.get_queryset().filter(processing_status='pending')
        serializer = self.get_serializer(pending_entries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def high_relevance(self, request):
        """Get high relevance context entries (relevance_score >= 70)"""
        high_relevance_entries = self.get_queryset().filter(relevance_score__gte=70)
        serializer = self.get_serializer(high_relevance_entries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def with_extracted_tasks(self, request):
        """Get context entries that have extracted tasks"""
        entries_with_tasks = self.get_queryset().exclude(extracted_tasks=[])
        serializer = self.get_serializer(entries_with_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Request AI analysis for a specific context entry"""
        context_entry = self.get_object()
        serializer = ContextAnalysisRequestSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            analysis_type = serializer.validated_data.get('analysis_type', 'full')
            force_reprocess = serializer.validated_data.get('force_reprocess', False)
            
            # Mock AI analysis response
            analysis_result = {
                'context_entry_id': context_entry.id,
                'analysis_type': analysis_type,
                'status': 'completed',
                'insights': {
                    'extracted_tasks': [
                        {
                            'title': 'Complete project presentation',
                            'description': 'Prepare slides for client meeting',
                            'suggested_deadline': '2024-12-28T15:00:00Z',
                            'priority_score': 85,
                            'confidence': 90
                        }
                    ],
                    'key_entities': ['project', 'presentation', 'client'],
                    'sentiment': {
                        'overall': 'neutral',
                        'urgency_level': 'medium',
                        'confidence': 75
                    },
                    'priority_indicators': [
                        'deadline mentioned',
                        'client meeting context'
                    ]
                },
                'relevance_score': 85.0,
                'processing_time': 1.2
            }
            
            # Update context entry with mock analysis
            context_entry.processing_status = 'completed'
            context_entry.relevance_score = analysis_result['relevance_score']
            context_entry.processed_insights = analysis_result['insights']
            context_entry.last_processed_at = timezone.now()
            context_entry.save()
            
            return Response(analysis_result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_analyze(self, request):
        """Request AI analysis for multiple context entries"""
        serializer = BulkContextAnalysisSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            context_entry_ids = serializer.validated_data['context_entry_ids']
            analysis_type = serializer.validated_data.get('analysis_type', 'full')
            
            entries = self.get_queryset().filter(id__in=context_entry_ids)
            
            # Mock bulk analysis response
            bulk_result = {
                'total_entries': len(entries),
                'analysis_type': analysis_type,
                'results': [
                    {
                        'context_entry_id': entry.id,
                        'status': 'completed',
                        'relevance_score': min(entry.relevance_score + 10, 100),
                        'extracted_tasks_count': 1
                    }
                    for entry in entries
                ],
                'summary': {
                    'high_relevance_count': len([e for e in entries if e.relevance_score >= 70]),
                    'total_extracted_tasks': len(entries),
                    'avg_relevance_score': entries.aggregate(
                        avg_score=Avg('relevance_score')
                    )['avg_score'] or 0
                }
            }
            
            return Response(bulk_result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get context summary statistics"""
        queryset = self.get_queryset()
        
        # Group by source type
        source_counts = queryset.values('source_type').annotate(
            count=Count('id')
        ).order_by('source_type')
        
        entries_by_source = {
            item['source_type']: item['count'] 
            for item in source_counts
        }
        
        # Recent activity (last 7 days)
        recent_entries = queryset.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        )
        
        summary_data = {
            'total_entries': queryset.count(),
            'entries_by_source': entries_by_source,
            'pending_processing': queryset.filter(processing_status='pending').count(),
            'high_relevance_entries': queryset.filter(relevance_score__gte=70).count(),
            'extracted_tasks_count': queryset.exclude(extracted_tasks=[]).count(),
            'avg_relevance_score': queryset.aggregate(
                avg_score=Avg('relevance_score')
            )['avg_score'] or 0,
            'recent_activity': [
                {
                    'id': entry.id,
                    'title': entry.title or f"{entry.source_type} entry",
                    'source_type': entry.source_type,
                    'timestamp': entry.timestamp,
                    'relevance_score': entry.relevance_score
                }
                for entry in recent_entries[:10]
            ]
        }
        
        serializer = ContextSummarySerializer(summary_data)
        return Response(serializer.data)


class ContextInsightViewSet(viewsets.ModelViewSet):
    """ViewSet for managing context insights"""
    serializer_class = ContextInsightSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['insight_type', 'is_actionable']
    ordering_fields = ['confidence_score', 'created_at']
    ordering = ['-confidence_score', '-created_at']

    def get_queryset(self):
        """Return insights for context entries belonging to the user"""
        return ContextInsight.objects.filter(context_entry__user=self.request.user)

    @action(detail=False, methods=['get'])
    def actionable(self, request):
        """Get actionable insights"""
        actionable_insights = self.get_queryset().filter(is_actionable=True)
        serializer = self.get_serializer(actionable_insights, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def high_confidence(self, request):
        """Get high confidence insights (confidence_score >= 80)"""
        high_confidence_insights = self.get_queryset().filter(confidence_score__gte=80)
        serializer = self.get_serializer(high_confidence_insights, many=True)
        return Response(serializer.data)
