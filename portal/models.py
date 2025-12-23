from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    EMPLOYMENT_TYPE=(
        ("full_time","Full time"),
        ("part_time","Part time"),
        ("internship","Internship"),
        ("contract","Contract"),
    )

    employer=models.ForeignKey(User,on_delete=models.CASCADE,related_name="jobs")
    title=models.CharField(max_length=200)
    company_name=models.CharField(max_length=255)
    location=models.CharField(max_length=255)
    description=models.TextField()
    requirements=models.TextField()
    salary =models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    employment_type=models.CharField(max_length=20,choices=EMPLOYMENT_TYPE,default="full_time")
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    last_date=models.DateField(blank=True,null=True)

    def __str__(self):
        return self.title



class Application(models.Model):
    STATUS_CHOICE=(
        ("applied","Applied"),
        ("shortlisted","Shortlisted"),
        ("rejected","Rejected"),
        ("hired","Hired"),
    )
    job=models.ForeignKey(Job,on_delete=models.CASCADE,related_name="applications")
    applicant=models.ForeignKey(User,on_delete=models.CASCADE,related_name="applications")
    cover_letter=models.TextField(blank=True)
    resume=models.FileField(upload_to="applications/",blank=True,null=True)
    applied_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,choices= STATUS_CHOICE,default="applied")
    def __str__(self):
        return f"{self.applicant.username} > {self.job.title}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_profile')
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    resume = models.FileField(upload_to='profiles/', blank=True, null=True)
    skills = models.TextField(blank=True, help_text="Comma-separated: Python, Django, React")
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"