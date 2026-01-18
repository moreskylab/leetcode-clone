from django.db import models
from django.contrib.auth import get_user_model
from problems.models import Problem

User = get_user_model()


class Submission(models.Model):
    """Model for code submissions"""
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Accepted', 'Accepted'),
        ('Wrong Answer', 'Wrong Answer'),
        ('Time Limit Exceeded', 'Time Limit Exceeded'),
        ('Memory Limit Exceeded', 'Memory Limit Exceeded'),
        ('Runtime Error', 'Runtime Error'),
        ('Compilation Error', 'Compilation Error'),
        ('Internal Error', 'Internal Error'),
    ]
    
    LANGUAGE_CHOICES = [
        ('python', 'Python 3'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('cpp', 'C++'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    
    code = models.TextField()
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    
    # Results
    runtime = models.IntegerField(null=True, blank=True)  # in milliseconds
    memory = models.IntegerField(null=True, blank=True)  # in KB
    error_message = models.TextField(blank=True)
    
    # Test case results
    passed_test_cases = models.IntegerField(default=0)
    total_test_cases = models.IntegerField(default=0)
    failed_test_case = models.JSONField(null=True, blank=True)  # Store details of first failed test
    
    # Judge0 token for tracking
    judge0_token = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['problem', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.status}"
    
    def update_problem_stats(self):
        """Update problem statistics after submission"""
        self.problem.total_submissions += 1
        if self.status == 'Accepted':
            self.problem.total_accepted += 1
        self.problem.update_acceptance_rate()
    
    def update_user_stats(self):
        """Update user statistics after accepted submission"""
        if self.status == 'Accepted':
            self.user.update_stats()
