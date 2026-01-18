from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Submission
from .serializers import (
    SubmissionSerializer,
    SubmissionCreateSerializer,
    SubmissionResultSerializer
)
from .judge0_service import Judge0Service
from problems.models import Problem, TestCase


class SubmissionCreateView(generics.CreateAPIView):
    """Create and execute a code submission"""
    
    serializer_class = SubmissionCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create submission
        submission = serializer.save(user=request.user, status='Processing')
        
        # Get problem and test cases
        problem = submission.problem
        test_cases = TestCase.objects.filter(problem=problem)
        
        if not test_cases.exists():
            submission.status = 'Internal Error'
            submission.error_message = 'No test cases found for this problem'
            submission.save()
            return Response(
                SubmissionResultSerializer(submission).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Execute submission
        try:
            judge0 = Judge0Service()
            passed = 0
            total = test_cases.count()
            submission.total_test_cases = total
            
            for test_case in test_cases:
                result = judge0.run_test_case(
                    code=submission.code,
                    language=submission.language,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output
                )
                
                if result['status'] == 'Accepted':
                    passed += 1
                else:
                    # Store first failed test case
                    if not submission.failed_test_case:
                        submission.failed_test_case = {
                            'input': test_case.input_data,
                            'expected': test_case.expected_output,
                            'output': result.get('stdout', ''),
                            'error': result.get('error_message', ''),
                            'is_sample': test_case.is_sample
                        }
                    
                    # Set submission status based on error type
                    submission.status = result['status']
                    submission.error_message = result.get('error_message', '')
                    break
            
            # Update submission results
            submission.passed_test_cases = passed
            
            if passed == total:
                submission.status = 'Accepted'
            
            # Save runtime and memory (use average or last test case)
            if result.get('runtime'):
                submission.runtime = int(float(result['runtime']) * 1000)  # Convert to ms
            if result.get('memory'):
                submission.memory = result['memory']
            
            submission.save()
            
            # Update statistics
            submission.update_problem_stats()
            if submission.status == 'Accepted':
                submission.update_user_stats()
            
        except Exception as e:
            submission.status = 'Internal Error'
            submission.error_message = str(e)
            submission.save()
        
        return Response(
            SubmissionResultSerializer(submission).data,
            status=status.HTTP_201_CREATED
        )


class SubmissionDetailView(generics.RetrieveAPIView):
    """Get submission details"""
    
    queryset = Submission.objects.all()
    serializer_class = SubmissionResultSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        # Users can only see their own submissions
        return self.queryset.filter(user=self.request.user)


class UserSubmissionsView(generics.ListAPIView):
    """List all submissions for a user"""
    
    serializer_class = SubmissionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user)


class ProblemSubmissionsView(generics.ListAPIView):
    """List all submissions for a specific problem by the current user"""
    
    serializer_class = SubmissionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        problem_id = self.kwargs.get('problem_id')
        return Submission.objects.filter(
            user=self.request.user,
            problem_id=problem_id
        )


class RunCodeView(APIView):
    """Run code against sample test cases without submitting"""
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request, problem_id):
        code = request.data.get('code')
        language = request.data.get('language')
        
        if not code or not language:
            return Response(
                {'error': 'Code and language are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get sample test cases
        problem = get_object_or_404(Problem, pk=problem_id)
        sample_tests = TestCase.objects.filter(problem=problem, is_sample=True)
        
        if not sample_tests.exists():
            return Response(
                {'error': 'No sample test cases found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Run against sample test cases
        try:
            judge0 = Judge0Service()
            results = []
            
            for test_case in sample_tests:
                result = judge0.run_test_case(
                    code=code,
                    language=language,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output
                )
                
                results.append({
                    'input': test_case.input_data,
                    'expected_output': test_case.expected_output,
                    'actual_output': result.get('stdout', ''),
                    'status': result['status'],
                    'runtime': result.get('runtime'),
                    'memory': result.get('memory'),
                    'error': result.get('error_message', ''),
                })
            
            return Response({'results': results}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
