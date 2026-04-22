from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Feedback, UserProfile, Department, Category, FeedbackResponse

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('user_type', 'department', 'phone_number', 'address', 'profile_picture')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

class FeedbackForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically update categories based on selected department
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['category'].queryset = Category.objects.filter(department_id=department_id).order_by('name')
            except (ValueError, TypeError):
                pass
    
    class Meta:
        model = Feedback
        fields = ('department', 'category', 'title', 'description', 'location', 'image', 'priority', 'anonymous')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the issue in detail...'}),
            'location': forms.TextInput(attrs={'placeholder': 'Street, Landmark, City'}),
            'title': forms.TextInput(attrs={'placeholder': 'Brief title of the issue'}),
        }

class FeedbackResponseForm(forms.ModelForm):
    class Meta:
        model = FeedbackResponse
        fields = ('response_text', 'action_taken', 'resolved_date')
        widgets = {
            'response_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your official response...'}),
            'action_taken': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe actions taken to resolve...'}),
            'resolved_date': forms.DateInput(attrs={'type': 'date'}),
        }

class FeedbackFilterForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="All Departments"
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Feedback.STATUS_CHOICES,
        required=False
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priority')] + Feedback.PRIORITY_CHOICES,
        required=False
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )