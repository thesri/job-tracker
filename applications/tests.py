from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Application, ResumeAnalysis, Resume
from django.urls import reverse
from unittest.mock import patch
# Create your tests here.
class ModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )

    def test_application_creation(self):
        app = Application.objects.create(
            user=self.user,
            company="Google",
            role="SWE",
            status="APPLIED",
            applied_date="2026-01-01"
        )
        self.assertEqual(app.company, "Google")
        self.assertEqual(app.user, self.user)

    def test_resume_analysis_creation(self):

        resume = Resume.objects.create(
            user=self.user,
            resume_file="dummy.pdf"
        )

        analysis = ResumeAnalysis.objects.create(
            user=self.user,
            resume=resume,
            job_description="Test JD",
            match_score=75,
            result_json={"match_score": 75}
        )

        self.assertEqual(analysis.match_score, 75)

class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )

    def test_home_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_home_loads_for_logged_in_user(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

class AnalyzeTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.client.login(username="testuser", password="testpass")
    @patch("applications.views.extract_text_from_pdf")
    @patch("applications.views.genai.GenerativeModel")
    def test_analyze_view(self, mock_model, mock_extract):
        mock_extract.return_value = "Python Django SQL"
        resume = Resume.objects.create(
            user=self.user,
            resume_file="dummy.pdf"
        )

        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value.text = """
        {
            "match_score": 80,
            "matching_skills": ["Python"],
            "missing_skills": ["Docker"],
            "suggestions": ["Learn Docker"]
        }
        """

        response = self.client.post(reverse('analyze_resume'), {
            "resume_id": resume.id,
            "job_desc": "Test job"
        })

        self.assertEqual(response.status_code, 200)