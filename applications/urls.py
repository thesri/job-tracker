from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('home/', views.home, name = 'home'),
    path('add/', views.add_application, name='add_application'),
    path('delete/<int:pk>/', views.delete_application, name='delete_application'),
    path('edit/<int:pk>/', views.edit_application, name='edit_application'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('resumes/', views.resume_list,name = 'resume_list'),
    path('resume/delete/<int:pk>/', views.delete_resume, name = 'delete_resume'),
    path('analyze/',views.analyze_resume,name='analyze_resume'),
    path('analysis/history/', views.analysis_history, name='analysis_history'),
    path('analysis/clear/', views.clear_analysis_history, name='clear_analysis_history'),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    path('', views.root, name = 'root'),
    
]