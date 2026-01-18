from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Statistics
    solved_count = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-points', '-solved_count']
        indexes = [
            models.Index(fields=['-points', '-solved_count']),
        ]
    
    def __str__(self):
        return self.username
    
    def update_stats(self):
        """Update user statistics based on accepted submissions"""
        from submissions.models import Submission
        
        # Count unique solved problems
        solved_problems = Submission.objects.filter(
            user=self,
            status='Accepted'
        ).values('problem').distinct().count()
        
        self.solved_count = solved_problems
        
        # Calculate points (Easy: 10, Medium: 20, Hard: 30)
        from problems.models import Problem
        solved_problem_ids = Submission.objects.filter(
            user=self,
            status='Accepted'
        ).values_list('problem_id', flat=True).distinct()
        
        total_points = 0
        for problem in Problem.objects.filter(id__in=solved_problem_ids):
            if problem.difficulty == 'Easy':
                total_points += 10
            elif problem.difficulty == 'Medium':
                total_points += 20
            elif problem.difficulty == 'Hard':
                total_points += 30
        
        self.points = total_points
        self.save()
