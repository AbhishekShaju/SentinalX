from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ExamViewSet, QuestionViewSet, AdminSettingsViewSet, ClassroomViewSet

router = DefaultRouter()
router.register(r'classrooms', ClassroomViewSet, basename='classroom')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'admin/settings', AdminSettingsViewSet, basename='admin-settings')

question_list = QuestionViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
question_detail = QuestionViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy',
})
question_bulk_create = QuestionViewSet.as_view({
    'post': 'bulk_create',
})

urlpatterns = [
    path('', include(router.urls)),
    path('exams/<int:exam_id>/questions/', question_list, name='exam-questions'),
    path('exams/<int:exam_id>/questions/<int:pk>/', question_detail, name='exam-question-detail'),
    path('exams/<int:exam_pk>/questions/bulk/', question_bulk_create, name='exam-questions-bulk'),
]

