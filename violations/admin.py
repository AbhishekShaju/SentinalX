from django.contrib import admin
from django.utils.html import format_html
from .models import Violation


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_info', 'violation_type_badge', 'timestamp', 'details_preview', 'resolved_badge']
    list_filter = ['violation_type', 'resolved', 'timestamp', 'session__exam']
    search_fields = ['session__student__username', 'session__exam__title', 'details', 'student__username']
    readonly_fields = ['session', 'student', 'violation_type', 'timestamp', 'details', 'created_at']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Violation Info', {
            'fields': ('session', 'student', 'violation_type', 'timestamp')
        }),
        ('Details', {
            'fields': ('details', 'resolved', 'created_at')
        }),
    )
    
    def session_info(self, obj):
        return f"{obj.session.exam.title} - {obj.session.student.username}"
    session_info.short_description = 'Session (Exam - Student)'
    session_info.admin_order_field = 'session__exam__title'
    
    def violation_type_badge(self, obj):
        colors = {
            'TAB_SWITCH': '#FFA500',
            'WINDOW_BLUR': '#FFA500',
            'MULTIPLE_FACES': '#DC3545',
            'NO_FACE_DETECTED': '#DC3545',
            'COPY_PASTE': '#DC3545',
            'RIGHT_CLICK': '#FFC107',
            'FUNCTION_KEY': '#FFC107',
            'CAMERA_ACCESS_DENIED': '#DC3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.violation_type, '#6C757D'),
            obj.get_violation_type_display()
        )
    violation_type_badge.short_description = 'Type'
    
    def resolved_badge(self, obj):
        if obj.resolved:
            return format_html(
                '<span style="background-color: #28A745; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">RESOLVED</span>'
            )
        return format_html(
            '<span style="background-color: #FFC107; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">PENDING</span>'
        )
    resolved_badge.short_description = 'Status'
    
    def details_preview(self, obj):
        if obj.details:
            return obj.details[:60] + "..." if len(obj.details) > 60 else obj.details
        return '-'
    details_preview.short_description = 'Details'
    
    def has_add_permission(self, request):
        return False

