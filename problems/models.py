from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Problem(models.Model):
    """Model for coding problems"""
    
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Problem details
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    
    # Constraints and examples
    constraints = models.TextField(blank=True)
    examples = models.JSONField(default=list, blank=True)  # List of example inputs/outputs
    
    # Code templates for different languages
    starter_code_python = models.TextField(blank=True)
    starter_code_javascript = models.TextField(blank=True)
    starter_code_java = models.TextField(blank=True)
    starter_code_cpp = models.TextField(blank=True)
    
    # Statistics
    acceptance_rate = models.FloatField(default=0.0)
    total_submissions = models.IntegerField(default=0)
    total_accepted = models.IntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_problems')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['difficulty']),
            models.Index(fields=['category']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.id}. {self.title}"
    
    def update_acceptance_rate(self):
        """Calculate and update acceptance rate"""
        if self.total_submissions > 0:
            self.acceptance_rate = round((self.total_accepted / self.total_submissions) * 100, 2)
        else:
            self.acceptance_rate = 0.0
        self.save()


class TestCase(models.Model):
    """Model for problem test cases"""
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)  # Whether to show to users
    is_hidden = models.BooleanField(default=False)  # Hidden test cases
    explanation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"Test Case {self.id} for {self.problem.title}"


class Solution(models.Model):
    """Model for official solutions"""
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='solutions')
    title = models.CharField(max_length=255)
    approach = models.TextField()
    code = models.TextField()
    language = models.CharField(max_length=50)
    time_complexity = models.CharField(max_length=100, blank=True)
    space_complexity = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"Solution for {self.problem.title} - {self.title}"
