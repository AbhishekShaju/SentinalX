from django.contrib import admin
from django.utils.html import format_html
from .models import ExamSession, Answer


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'exam_title', 'student_name', 'status_badge', 'score_display', 'violation_count', 'started_at', 'ended_at']
    list_filter = ['status', 'started_at', 'ended_at', 'exam__teacher']
    search_fields = ['exam__title', 'student__username', 'student__first_name', 'student__last_name', 'student__email']
    readonly_fields = ['started_at', 'ended_at', 'total_marks', 'violation_count_display']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Session Info', {
            'fields': ('exam', 'student', 'status')
        }),
        ('Timing', {
            'fields': ('started_at', 'ended_at')
        }),
        ('Results', {
            'fields': ('total_marks', 'violation_count_display')
        }),
    )
    
    def exam_title(self, obj):
        return obj.exam.title
    exam_title.short_description = 'Exam'
    exam_title.admin_order_field = 'exam__title'
    
    def student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name} ({obj.student.username})"
    student_name.short_description = 'Student'
    student_name.admin_order_field = 'student__username'
    
    def status_badge(self, obj):
        colors = {
            'IN_PROGRESS': '#FFA500',
            'COMPLETED': '#28A745',
            'TERMINATED': '#DC3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6C757D'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def score_display(self, obj):
        if obj.status == 'COMPLETED':
            # Calculate score from answers
            score = sum(answer.marks_awarded for answer in obj.answers.all())
            percentage = (score / obj.total_marks * 100) if obj.total_marks > 0 else 0
            color = '#28A745' if percentage >= 60 else '#DC3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}/{} ({}%)</span>',
                color,
                score,
                obj.total_marks,
                round(percentage, 1)
            )
        return '-'
    score_display.short_description = 'Score'
    
    def violation_count(self, obj):
        count = obj.violations.count()
        color = '#28A745' if count == 0 else '#FFA500' if count <= 3 else '#DC3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            count
        )
    violation_count.short_description = 'Violations'
    
    def violation_count_display(self, obj):
        return obj.violations.count()
    violation_count_display.short_description = 'Total Violations'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_exam', 'session_student', 'question_text', 'answer_display', 'marks_awarded']
    list_filter = ['session__exam', 'session__status']
    search_fields = ['session__student__username', 'session__exam__title', 'question__text']
    readonly_fields = ['session', 'question', 'mcq_choice', 'short_text', 'marks_awarded']
    
    def session_exam(self, obj):
        return obj.session.exam.title
    session_exam.short_description = 'Exam'
    session_exam.admin_order_field = 'session__exam__title'
    
    def session_student(self, obj):
        return obj.session.student.username
    session_student.short_description = 'Student'
    session_student.admin_order_field = 'session__student__username'
    
    def question_text(self, obj):
        text = obj.question.text
        return text[:50] + "..." if len(text) > 50 else text
    question_text.short_description = 'Question'
    
    def answer_display(self, obj):
        if obj.question.type == 'MCQ' or obj.question.type == 'TRUE_FALSE':
            choices = obj.question.choices or []
            if obj.mcq_choice is not None and obj.mcq_choice < len(choices):
                return choices[obj.mcq_choice]
            return f"Choice {obj.mcq_choice}"
        return obj.short_text[:50] if obj.short_text else '-'
    answer_display.short_description = 'Answer'
    
    def has_add_permission(self, request):
        return False

