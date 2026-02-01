"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/problems/', include('problems.urls')),
    path('api/submissions/', include('submissions.urls')),

    # Frontend routes
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('problems/', TemplateView.as_view(template_name='problems/list.html'),
         name='problem_list'),
    path('problems/<int:pk>/',
         TemplateView.as_view(template_name='problems/detail.html'), name='problem_detail'),
    path('leaderboard/', TemplateView.as_view(template_name='leaderboard.html'),
         name='leaderboard'),
    path('login/', TemplateView.as_view(template_name='auth/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='auth/register.html'), name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
