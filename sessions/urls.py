from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ExamSessionViewSet

router = DefaultRouter()
router.register(r'sessions', ExamSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
    path('exams/<int:exam_id>/start/', ExamSessionViewSet.as_view({'post': 'start_exam'}), name='exam-start'),
    path('exams/<int:exam_id>/submit/', ExamSessionViewSet.as_view({'post': 'submit_exam'}), name='exam-submit'),
]

