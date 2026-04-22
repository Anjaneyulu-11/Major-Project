# forms.py
from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'name', 'email', 'phone', 'address',
            'category', 'sub_category', 'details',
            'city', 'pincode', 'image'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'Enter your full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'example@email.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+91 9876543210'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your address'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'categorySelect',
                'required': True
            }),
            'sub_category': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Road Repair, Power Outage'
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6,
                'id': 'complaintDetails',
                'placeholder': 'Please describe your issue in detail...',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your city or district',
                'required': True
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '6-digit PIN code'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['category'].required = True
        self.fields['details'].required = True
        self.fields['city'].required = True
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validate file size (5MB max)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size must be under 5MB")
            
            # Validate file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            extension = image.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError("Only JPG, PNG, and GIF files are allowed")
        
        return image