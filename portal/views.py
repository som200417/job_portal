from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView,CreateView,DetailView,TemplateView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .mixins import EmployerRequiredMixin
from django.urls import reverse_lazy
from .forms import ApplyForm,ApplicationStatusForm,ProfileForm
from .models import Job,Application,Profile
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer,ProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count,Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

@api_view(['POST'])
def update_application_status(request, job_id, pk):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    application = get_object_or_404(Application, id=pk, job=job)
    
    new_status = request.data.get('status')
    if new_status in dict(Application.STATUS_CHOICE):
        application.status = new_status
        application.save()
        return Response({'status': application.get_status_display()})
    
    return Response({'error': 'Invalid status'}, status=400)
class ApplyJobView(LoginRequiredMixin, UserPassesTestMixin, CreateView):  
    model = Application
    form_class = ApplyForm
    template_name = 'jobs/job_detail.html'
    
    def test_func(self):  
        return not self.request.user.jobs.exists()  # Seeker only
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = get_object_or_404(Job, pk=self.kwargs['pk'])  # ✅ FIXED: self.kwargs['pk']
        context['job'] = job
        
        already_applied = Application.objects.filter(
            job=job, 
            applicant=self.request.user
        ).exists()
        context['already_applied'] = already_applied
        return context
    
    def form_valid(self, form):
        job = get_object_or_404(Job, pk=self.kwargs['pk'])  # ✅ FIXED: self.kwargs['pk']
        
        if Application.objects.filter(job=job, applicant=self.request.user).exists():
            messages.error(self.request, "You have already applied for this job!")
            return redirect('job_detail', pk=job.pk)
            
        if job.last_date and job.last_date < timezone.now().date():
            messages.error(self.request, "This job posting has expired!")
            return redirect('job_detail', pk=job.pk)
        
        form.instance.job = job
        form.instance.applicant = self.request.user
        messages.success(self.request, "Application submitted successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('application_success')


class EmployerDashboardView(LoginRequiredMixin, EmployerRequiredMixin, ListView): 
    model = Job
    template_name = 'jobs/employer_dashboard.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user).annotate(
            applications_count=Count('applications')
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_applications'] = self.object_list.aggregate(
            total=Sum('applications_count')
        )['total'] or 0 
        return context
        
class JobCreateView(LoginRequiredMixin, EmployerRequiredMixin, CreateView): 
    model = Job
    fields = ['title', 'company_name', 'location', 'description', 
              'requirements', 'salary', 'employment_type', 'last_date']
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('employer_dashboard') 
    
    def form_valid(self, form):
        form.instance.employer = self.request.user
        form.instance.is_active = True
        return super().form_valid(form)


class JobListView(ListView):
    model=Job
    template_name='jobs/job_list.html'
    context_object_name='jobs'
    paginate_by=9
    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True).select_related('employer').order_by('-created_at')
        

        query = self.request.GET.get('q')
        location = self.request.GET.get('location')
        employment_type = self.request.GET.get('employment_type')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |          
                Q(company_name__icontains=query) |   
                Q(description__icontains=query)      
            )
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['location'] = self.request.GET.get('location', '')
        context['employment_type'] = self.request.GET.get('employment_type', '')
        return context
    


class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    
    def post(self, request, *args, **kwargs):
        # ✅ HANDLE POST in SAME view
        self.object = self.get_object()
        form = ApplyForm(request.POST, request.FILES)
        if form.is_valid():
            job = self.object
            
            # Duplicate check
            if Application.objects.filter(job=job, applicant=request.user).exists():
                messages.error(request, "You have already applied for this job!")
                return self.render_to_response(self.get_context_data())
            
            if job.last_date and job.last_date < timezone.now().date():
                messages.error(request, "This job posting has expired!")
                return self.render_to_response(self.get_context_data())
            
            # Save application
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('application_success')
        else:
            # Invalid form
            context = self.get_context_data(form=form)
            return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.object
        
        if self.request.user.is_authenticated and not self.request.user.jobs.exists():
            # ✅ Pass form (handle POST errors)
            form = kwargs.get('form', ApplyForm())
            context['form'] = form
            context['already_applied'] = Application.objects.filter(
                job=job, applicant=self.request.user
            ).exists()
        else:
            context['already_applied'] = False
            
        context['applications_count'] = job.applications.count()
        return context


class EmployerApplicationView(LoginRequiredMixin, EmployerRequiredMixin, ListView):
    model = Application 
    template_name = 'jobs/employer_application.html'
    context_object_name = 'applications'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_id = self.kwargs.get('job_id')
        if job_id:
            context['job'] = get_object_or_404(
                Job, id=job_id, employer=self.request.user  # ✅ User, NOT profile
            )
        return context
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        if job_id:
            job = get_object_or_404( Job, id=job_id, employer=self.request.user)
            return job.applications.all().select_related(
                'applicant', 'job' ).order_by('-applied_at')  
        return Application.objects.filter(job__employer=self.request.user).select_related('applicant', 'job').order_by('-applied_at')

class UpdateApplicationStatusView(LoginRequiredMixin, EmployerRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationStatusForm
    template_name = 'jobs/update_status.html'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return Application.objects.filter(
            job_id=job_id, 
            job__employer=self.request.user
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = get_object_or_404(Job, id=self.kwargs['job_id'], employer=self.request.user)
        context['application'] = self.get_object()
        return context
    
    def get_success_url(self):
        return reverse_lazy('jobs:employer_job_applications', kwargs={'job_id': self.kwargs['job_id']})
class SeekerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'jobs/seeker_dashboard.html'
    
    def test_func(self):

        return not hasattr(self.request.user, 'jobs') or self.request.user.jobs.count() == 0
    
    def get_context_data(self, **kwargs):     
        context = super().get_context_data(**kwargs)
        context['recent_jobs'] = Job.objects.filter(is_active=True).select_related('employer')[:6]
        context['applied_count'] = self.request.user.applications.count()
        return context

class SeekerApplicationsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Application
    template_name = 'jobs/seeker_applications.html'
    context_object_name = 'applications'
    paginate_by = 10
    
    def test_func(self):
        return not hasattr(self.request.user, 'jobs') or self.request.user.jobs.count() == 0
    
    def get_queryset(self):
        return self.request.user.applications.select_related('job', 'job__employer').order_by('-applied_at')
class ApplicationSuccessView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'jobs/application_success.html'
    
    def test_func(self):
        return not self.request.user.jobs.exists()  # Seeker only
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the LAST application (most recent)
        recent_application = Application.objects.filter(
            applicant=self.request.user
        ).select_related('job').order_by('-applied_at').first()
        
        if recent_application:
            context['application'] = recent_application
            context['job'] = recent_application.job
            context['total_applications'] = self.request.user.applications.count()
        else:
            context['total_applications'] = 0
            
        return context
    
class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'jobs/profile_update.html'
    
    def test_func(self):
        return not self.request.user.jobs.exists()
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_success_url(self):
        messages.success(self.request, "Profile updated successfully!")
        return reverse_lazy('jobs:seeker_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills_list'] = self.object.skills.split(',') if self.object.skills else []
        return context
    def form_valid(self, form):
        response = super().form_valid(form)
      
        refresh = RefreshToken.for_user(self.request.user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'message': 'Profile updated!'
        })
    
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile