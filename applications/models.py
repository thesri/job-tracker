from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ("APPLIED", "Applied"),
        ("OA", "Online Assessment"),
        ("INTERVIEW", "Interview"),
        ("OFFER", "Offer"),
        ("REJECTED", "Rejected"),
    ]
    company = models.CharField(max_length = 255)
    role = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="APPLIED")
    applied_date = models.DateField()
    job_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.company} - {self.role}"
    
class Resume(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=100)

    resume_file = models.FileField(
        upload_to='resumes/'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    
class ResumeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_description = models.TextField()
    match_score = models.IntegerField()
    result_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)