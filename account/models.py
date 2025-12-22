from django.db import models

from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICE=(
        ("employer","Employer"),
        ("job_seeker","Job Seeker")
    )

    user= models.OneToOneField(User,on_delete=models.CASCADE, related_name="profile")
    role= models.CharField(max_length=20,choices=ROLE_CHOICE,default="job_seeker")
    phone=models.CharField(max_length=20,blank=True)
    resume=models.FileField(upload_to="resumes/",blank=True,null=True)

    def __str__(self):
        return f"{self.user.username}({self.role})"