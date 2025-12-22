from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

class EmployerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:  # ✅ Fixed: not (was if)
            return False
        try:
            return self.request.user.profile.role == "employer"  # ✅ Fixed: == not =
        except:
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, "Only employers can access this page.")
        return redirect('job_list')

class JobSeekerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profile.role == 'job_seeker'
        except:
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, "Only job seekers can access this page.")
        return redirect('job_list')
