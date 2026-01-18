from django.contrib import admin
from .models import Problem, TestCase, Solution


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1


class SolutionInline(admin.StackedInline):
    model = Solution
    extra = 0


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty', 'category', 'acceptance_rate', 'total_submissions', 'is_active')
    list_filter = ('difficulty', 'category', 'is_active')
    search_fields = ('title', 'description', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TestCaseInline, SolutionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'difficulty', 'category', 'tags')
        }),
        ('Problem Details', {
            'fields': ('constraints', 'examples')
        }),
        ('Starter Code', {
            'fields': ('starter_code_python', 'starter_code_javascript', 'starter_code_java', 'starter_code_cpp'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('acceptance_rate', 'total_submissions', 'total_accepted'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'is_active')
        }),
    )


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'is_sample', 'is_hidden')
    list_filter = ('is_sample', 'is_hidden', 'problem__difficulty')
    search_fields = ('problem__title',)


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'title', 'language')
    list_filter = ('language', 'problem__difficulty')
    search_fields = ('problem__title', 'title')
