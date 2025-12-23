from django import forms
from .models import Application,Profile

class ApplyForm(forms.ModelForm): 
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us why you are perfect for this role...'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            })
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("Resume size should be less than 5MB")
            ext = resume.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise forms.ValidationError("Only PDF, DOC, DOCX allowed")
        return resume


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            })
        }
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'bio', 'linkedin', 'github', 'resume', 'skills']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Tell employers about your experience...'
            }),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'github': forms.URLInput(attrs={'class': 'form-control'}),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, Django, JavaScript, React...'
            }),
        }  