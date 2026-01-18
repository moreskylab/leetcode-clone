from rest_framework import serializers
from .models import Submission
from problems.serializers import ProblemListSerializer


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model"""
    
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Submission
        fields = ('id', 'user', 'user_username', 'problem', 'problem_title',
                  'code', 'language', 'status', 'runtime', 'memory',
                  'error_message', 'passed_test_cases', 'total_test_cases',
                  'failed_test_case', 'created_at')
        read_only_fields = ('id', 'user', 'status', 'runtime', 'memory',
                            'error_message', 'passed_test_cases', 'total_test_cases',
                            'failed_test_case', 'created_at')


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating submissions"""
    
    class Meta:
        model = Submission
        fields = ('problem', 'code', 'language')
    
    def validate_language(self, value):
        valid_languages = ['python', 'javascript', 'java', 'cpp']
        if value not in valid_languages:
            raise serializers.ValidationError(f"Language must be one of: {', '.join(valid_languages)}")
        return value


class SubmissionResultSerializer(serializers.ModelSerializer):
    """Detailed serializer for submission results"""
    
    problem = ProblemListSerializer(read_only=True)
    
    class Meta:
        model = Submission
        fields = ('id', 'problem', 'code', 'language', 'status', 'runtime',
                  'memory', 'error_message', 'passed_test_cases', 'total_test_cases',
                  'failed_test_case', 'created_at')
