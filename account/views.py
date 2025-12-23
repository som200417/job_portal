from django.shortcuts import render,redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignupForm
from .models import UserProfile
from django.contrib.auth import logout
from django.contrib import messages

class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        UserProfile.objects.create(
            user=user,
            role=form.cleaned_data['role'],
            phone=form.cleaned_data.get('phone', '')  # ✅ Safe default
        )
        return super().form_valid(form)


def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('jobs:job_list')