from django.contrib import admin
from .models import Application,Job
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display=[
        'title','company_name','location','is_active','created_at'
    ]
    list_filter=[
        'is_active','employment_type'
    ]
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display=['applicant','job','status','applied_at']
    list_filter=['status']