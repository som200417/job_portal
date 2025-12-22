from django.urls import path, re_path
from . import views

app_name = 'jobs'  

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    re_path(r'^(?P<pk>\d+)/([^/]+)/?$', views.JobDetailView.as_view(), name='job_detail_slug'),
    path('apply/<int:pk>/', views.ApplyJobView.as_view(), name='apply_job'),
    path('applied/', views.ApplicationSuccessView.as_view(), name='application_success'),

    path('employer/', views.EmployerDashboardView.as_view(), name='employer_dashboard'),
    path('employer/create/', views.JobCreateView.as_view(), name='job_create'),
    path('employer/applications/', views.EmployerApplicationView.as_view(), name='employer_all_applications'),
    path('employer/applications/<int:job_id>/', views.EmployerApplicationView.as_view(), name='employer_job_applications'),
    path('employer/applications/<int:job_id>/<int:pk>/status/', views.UpdateApplicationStatusView.as_view(), name='update_application_status'),
    path('seeker/', views.SeekerDashboardView.as_view(), name='seeker_dashboard'),
    path('seeker/applications/', views.SeekerApplicationsView.as_view(), name='seeker_applications'),
]
