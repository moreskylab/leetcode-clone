from django.urls import path
from .views import (
    SubmissionCreateView,
    SubmissionDetailView,
    UserSubmissionsView,
    ProblemSubmissionsView,
    RunCodeView
)

urlpatterns = [
    # Submissions
    path('', SubmissionCreateView.as_view(), name='submission_create'),
    path('<int:pk>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('user/', UserSubmissionsView.as_view(), name='user_submissions'),
    path('problem/<int:problem_id>/', ProblemSubmissionsView.as_view(), name='problem_submissions'),
    
    # Run code without submitting
    path('run/<int:problem_id>/', RunCodeView.as_view(), name='run_code'),
]
