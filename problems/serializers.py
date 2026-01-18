from rest_framework import serializers
from .models import Problem, TestCase, Solution


class TestCaseSerializer(serializers.ModelSerializer):
    """Serializer for TestCase model"""
    
    class Meta:
        model = TestCase
        fields = ('id', 'input_data', 'expected_output', 'is_sample', 'explanation')


class SolutionSerializer(serializers.ModelSerializer):
    """Serializer for Solution model"""
    
    class Meta:
        model = Solution
        fields = ('id', 'title', 'approach', 'code', 'language', 
                  'time_complexity', 'space_complexity')


class ProblemListSerializer(serializers.ModelSerializer):
    """Serializer for problem list view"""
    
    is_solved = serializers.SerializerMethodField()
    
    class Meta:
        model = Problem
        fields = ('id', 'title', 'slug', 'difficulty', 'category', 
                  'tags', 'acceptance_rate', 'is_solved')
    
    def get_is_solved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from submissions.models import Submission
            return Submission.objects.filter(
                user=request.user,
                problem=obj,
                status='Accepted'
            ).exists()
        return False


class ProblemDetailSerializer(serializers.ModelSerializer):
    """Serializer for problem detail view"""
    
    test_cases = serializers.SerializerMethodField()
    solutions = SolutionSerializer(many=True, read_only=True)
    is_solved = serializers.SerializerMethodField()
    user_submissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Problem
        fields = ('id', 'title', 'slug', 'description', 'difficulty', 'category',
                  'tags', 'constraints', 'examples', 'starter_code_python',
                  'starter_code_javascript', 'starter_code_java', 'starter_code_cpp',
                  'acceptance_rate', 'total_submissions', 'total_accepted',
                  'test_cases', 'solutions', 'is_solved', 'user_submissions_count')
    
    def get_test_cases(self, obj):
        # Only return sample test cases to users
        sample_cases = obj.test_cases.filter(is_sample=True, is_hidden=False)
        return TestCaseSerializer(sample_cases, many=True).data
    
    def get_is_solved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from submissions.models import Submission
            return Submission.objects.filter(
                user=request.user,
                problem=obj,
                status='Accepted'
            ).exists()
        return False
    
    def get_user_submissions_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from submissions.models import Submission
            return Submission.objects.filter(
                user=request.user,
                problem=obj
            ).count()
        return 0
