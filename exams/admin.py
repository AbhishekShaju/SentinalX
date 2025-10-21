from django.contrib import admin
from .models import Classroom, ClassroomMembership, Exam, Question, AdminSettings


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'classroom_id', 'teacher', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'teacher']
    search_fields = ['name', 'classroom_id', 'teacher__username']
    readonly_fields = ['classroom_id', 'created_at', 'updated_at']


@admin.register(ClassroomMembership)
class ClassroomMembershipAdmin(admin.ModelAdmin):
    list_display = ['classroom', 'student', 'joined_at', 'is_active']
    list_filter = ['is_active', 'joined_at']
    search_fields = ['classroom__name', 'student__username']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'classroom', 'duration_minutes', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at', 'teacher', 'classroom']
    search_fields = ['title', 'teacher__username', 'classroom__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'type', 'text_preview', 'marks', 'order']
    list_filter = ['type', 'exam']
    search_fields = ['text', 'exam__title']
    ordering = ['exam', 'order']

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Question Text"


@admin.register(AdminSettings)
class AdminSettingsAdmin(admin.ModelAdmin):
    list_display = ['default_violation_limit', 'updated_at']
