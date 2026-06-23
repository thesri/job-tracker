from django.shortcuts import render, redirect, get_object_or_404
from .models import Application, Resume, ResumeAnalysis
from django.contrib.auth.decorators import login_required
from .forms import ResumeForm
from pypdf import PdfReader
import google.generativeai as genai
from django.conf import settings
import json 
import re
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect
genai.configure(api_key=settings.GEMINI_API_KEY)
# Create your views here.
@login_required
def home(request):
    
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    resume_count = Resume.objects.filter(user = request.user).count()
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    if status_filter:
        applications = applications.filter(status=status_filter)
    if search_query:
        applications = applications.filter(company__icontains = search_query)
    total = applications.count()
    oa = applications.filter(status="OA").count()
    interviews = applications.filter(status="INTERVIEW").count()
    offers = applications.filter(status="OFFER").count()
    applied = total - (oa + interviews + offers)
    print("USER:", request.user)
    print("AUTH:", request.user.is_authenticated)
    return render(request, 'applications/home.html', {
        'applications': applications,
        'status_filter': status_filter,
        'search_query': search_query,
        'applied': applied,
        'total': total,
        'oa': oa,
        'interviews': interviews,
        'offers': offers,
        'resume_count': resume_count,
    })
@login_required
def add_application(request):
    if request.method == "POST":
        user = request.user
        company = request.POST.get("company")
        role = request.POST.get("role")
        status = request.POST.get("status")
        applied_date = request.POST.get("applied_date")
        job_link = request.POST.get("job_link")
        notes = request.POST.get("notes")

        Application.objects.create(
            user = user,
            company=company,
            role=role,
            status=status,
            applied_date=applied_date,
            job_link=job_link,
            notes=notes
        )
        return redirect("home")

    return render(request, "applications/add.html")
@login_required
def delete_application(request, pk):
    application = get_object_or_404(Application, id=pk, user = request.user)
    application.delete()
    return redirect('home')
@login_required
def edit_application(request, pk):
    application = get_object_or_404(Application, id=pk, user = request.user)

    if request.method == "POST":
        application.company = request.POST.get("company")
        application.role = request.POST.get("role")
        application.status = request.POST.get("status")
        application.applied_date = request.POST.get("applied_date")
        application.job_link = request.POST.get("job_link")
        application.notes = request.POST.get("notes")

        application.save()
        return redirect('home')

    return render(request, 'applications/edit.html', {'application': application})

@login_required
def upload_resume(request):
    if request.method == "POST":
        form = ResumeForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()

            return redirect('home')

    else:
        form = ResumeForm()

    return render(
        request,
        'applications/upload_resume.html',
        {'form': form}
    )
@login_required
def resume_list(request):
    resumes = Resume.objects.filter(
        user=request.user
    ).order_by('-uploaded_at')

    return render(
        request,
        'applications/resume_list.html',
        {'resumes': resumes}
    )
@login_required
def delete_resume(request, pk):
    resume = get_object_or_404(
        Resume,
        id=pk,
        user=request.user
    )

    resume.delete()

    return redirect('resume_list')
@login_required
def analyze_resume(request):
    resumes = Resume.objects.filter(user=request.user)

    result = None

    if request.method == "POST":
        resume_id = request.POST.get("resume_id")
        job_desc = request.POST.get("job_desc")

        selected_resume = Resume.objects.get(
            id=resume_id,
            user=request.user
        )
        resume_text = extract_text_from_pdf(
        selected_resume.resume_file
        )
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        You are an AI resume reviewer.

        Compare the resume with the job description.

        Return ONLY valid JSON in this format:

        {{
        "match_score": 0,
        "matching_skills": [],
        "missing_skills": [],
        "suggestions": []
        }}
        

        Resume:
        {resume_text}

        Job Description:
        {job_desc}
        """
        response = model.generate_content(prompt)
        raw = response.text.strip()


        match = re.search(r"\{.*\}", raw, re.DOTALL)

        if match:
            cleaned = match.group()
            result = json.loads(cleaned)
        else:
            result = {
                "match_score": 0,
                "matching_skills": [],
                "missing_skills": [],
                "suggestions": [],
                "error": "Invalid AI response"
            }
        
        ResumeAnalysis.objects.create(
            user=request.user,
            resume=selected_resume,
            job_description=job_desc,
            match_score=result.get("match_score", 0) if isinstance(result,dict) else 0,
            result_json=result
        )
        # print(response.text)
        # print(type(result))
    return render(request, "applications/analyze.html", {
        "resumes": resumes,
        "result": result
    })
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text
@login_required
def analysis_history(request):
    history = ResumeAnalysis.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, "applications/analysis_history.html", {
        "history": history
    })
@login_required
def clear_analysis_history(request):
    if request.method == "POST":
        ResumeAnalysis.objects.filter(user=request.user).delete()

    return redirect('analysis_history')

from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "applications/signup.html", {
                "error": "Username already exists"
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)
        return redirect("home")

    return render(request, "applications/signup.html")
def root(request):
    if request.user.is_authenticated:
        return redirect("home")
    return redirect("signup")