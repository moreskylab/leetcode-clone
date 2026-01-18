from django.urls import path
from .views import ProblemListView, ProblemDetailView, ProblemTestCasesView

urlpatterns = [
    path('', ProblemListView.as_view(), name='problem_list'),
    path('<int:pk>/', ProblemDetailView.as_view(), name='problem_detail'),
    path('<int:pk>/test-cases/', ProblemTestCasesView.as_view(), name='problem_test_cases'),
]
