from rest_framework import generics, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Problem, TestCase
from .serializers import ProblemListSerializer, ProblemDetailSerializer, TestCaseSerializer


class ProblemListView(generics.ListAPIView):
    """List all problems with filtering and search"""
    
    queryset = Problem.objects.filter(is_active=True)
    serializer_class = ProblemListSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'category']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['id', 'difficulty', 'acceptance_rate', 'total_submissions']
    ordering = ['id']


class ProblemDetailView(generics.RetrieveAPIView):
    """Get problem details by ID or slug"""
    
    queryset = Problem.objects.filter(is_active=True)
    serializer_class = ProblemDetailSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'pk'
    
    def get_object(self):
        # Support lookup by both ID and slug
        lookup_value = self.kwargs.get(self.lookup_field)
        try:
            # Try to find by ID first
            return self.queryset.get(pk=int(lookup_value))
        except (ValueError, Problem.DoesNotExist):
            # Fall back to slug
            return self.queryset.get(slug=lookup_value)


class ProblemTestCasesView(generics.ListAPIView):
    """Get all test cases for a problem (including hidden ones for submission validation)"""
    
    serializer_class = TestCaseSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        problem_id = self.kwargs.get('pk')
        # Return all test cases (including hidden) for server-side validation
        return TestCase.objects.filter(problem_id=problem_id)
