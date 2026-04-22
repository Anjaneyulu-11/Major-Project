from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random
import string


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    head = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Department"
        verbose_name_plural = "Departments"


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
        ('On Hold', 'On Hold'),
        ('Escalated', 'Escalated'),
    ]
    
    CATEGORY_CHOICES = [
        ('Municipal Issues', 'Municipal Issues'),
        ('Electricity', 'Electricity'),
        ('Water Supply', 'Water Supply'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Transport', 'Transport'),
        ('Waste Management', 'Waste Management'),
        ('Road Infrastructure', 'Road Infrastructure'),
        ('Public Safety', 'Public Safety'),
        ('General', 'General'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    
    # Complaint details
    complaint_id = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Location details
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    landmark = models.CharField(max_length=200, blank=True, null=True)
    
    # Complaint information
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='General')
    sub_category = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    details = models.TextField()
    
    # AI Analysis fields
    ai_category = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    sentiment_score = models.FloatField(default=0.0)
    sentiment_label = models.CharField(max_length=20, default='Neutral')
    keywords = models.TextField(blank=True, null=True)
    urgency_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_complaints')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='complaints')
    escalation_level = models.IntegerField(default=0)
    
    # Media
    image = models.ImageField(upload_to='complaints/images/%Y/%m/%d/', blank=True, null=True)
    document = models.FileField(upload_to='complaints/documents/%Y/%m/%d/', blank=True, null=True)
    video = models.FileField(upload_to='complaints/videos/%Y/%m/%d/', blank=True, null=True)
    
    # Timestamps with timezone
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    
    # Feedback
    citizen_feedback = models.TextField(blank=True, null=True)
    citizen_rating = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    resolution_notes = models.TextField(blank=True, null=True)
    
    # Anonymous complaint option
    is_anonymous = models.BooleanField(default=False)
    
    # Tracking
    view_count = models.PositiveIntegerField(default=0)
    upvotes = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.complaint_id:
            date_str = timezone.now().strftime("%Y%m%d")
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.complaint_id = f"CGR{date_str}{random_str}"
        
        if self.status == 'Resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'Resolved':
            self.resolved_at = None
            
        # Auto-generate title if not provided
        if not self.title:
            self.title = f"{self.category} Complaint - {self.complaint_id}"
            
        super().save(*args, **kwargs)
        
        # Update user profile statistics if user exists
        if self.user and self.user.pk:
            from django.apps import apps
            try:
                UserProfile = apps.get_model('chatbot', 'UserProfile')
                profile = UserProfile.objects.filter(user=self.user).first()
                if profile:
                    profile.update_statistics()
            except:
                pass  # Silently fail if UserProfile doesn't exist
    
    def send_registration_email(self):
        """Send email notification when complaint is registered"""
        # Check if email backend is configured
        if not hasattr(settings, 'EMAIL_BACKEND'):
            print("Email backend not configured in settings.py")
            return False
        
        subject = f'Your Complaint Registered - ID: {self.complaint_id}'
        
        # HTML email content
        try:
            html_message = render_to_string('emails/complaint_registered.html', {
                'name': self.display_name,
                'complaint_id': self.complaint_id,
                'complaint_title': self.title,
                'complaint_details': self.details[:500] + "..." if len(self.details) > 500 else self.details,
                'category': self.get_category_display(),
                'created_date': self.created_at.strftime("%d %B, %Y"),
                'track_url': f"{getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')}/track-complaint/"
            })
        except:
            # Fallback if template doesn't exist
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Complaint Registered Successfully</h2>
                <p><strong>Name:</strong> {self.display_name}</p>
                <p><strong>Complaint ID:</strong> {self.complaint_id}</p>
                <p><strong>Category:</strong> {self.get_category_display()}</p>
                <p><strong>Date:</strong> {self.created_at.strftime('%d %B, %Y')}</p>
                <p>You can track your complaint using this ID.</p>
            </body>
            </html>
            """
        
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@publicpulse.com'),
                recipient_list=[self.email],
                html_message=html_message,
                fail_silently=True,  # Don't crash if email fails
            )
            print(f"Email sent successfully to {self.email} for complaint {self.complaint_id}")
            return True
        except Exception as e:
            # Log the error but don't fail the complaint submission
            print(f"Email sending failed for {self.complaint_id}: {str(e)}")
            return False
    
    def send_status_update_email(self, update_text, updated_by="System"):
        """Send email when complaint status is updated"""
        subject = f'Complaint Update - {self.complaint_id}'
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h2>Complaint Status Updated</h2>
            <p><strong>Complaint ID:</strong> {self.complaint_id}</p>
            <p><strong>New Status:</strong> {self.get_status_display()}</p>
            <p><strong>Update:</strong> {update_text}</p>
            <p><strong>Updated by:</strong> {updated_by}</p>
            <p><strong>Date:</strong> {timezone.now().strftime('%d %B, %Y %H:%M')}</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@publicpulse.com'),
                recipient_list=[self.email],
                html_message=html_message,
                fail_silently=True,
            )
            return True
        except Exception as e:
            print(f"Status update email failed: {str(e)}")
            return False
    
    @property
    def days_open(self):
        if self.resolved_at:
            return (self.resolved_at - self.created_at).days
        return (timezone.now() - self.created_at).days
    
    @property
    def is_overdue(self):
        if self.deadline and not self.resolved_at:
            return timezone.now() > self.deadline
        return False
    
    @property
    def display_name(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.name
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def __str__(self):
        return f"{self.complaint_id} - {self.display_name} - {self.category} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['category', 'created_at']),
            models.Index(fields=['department', 'status']),
        ]
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"


class ComplaintUpdate(models.Model):
    TYPE_CHOICES = [
        ('status_update', 'Status Update'),
        ('note', 'Note'),
        ('escalation', 'Escalation'),
        ('assignment', 'Assignment'),
        ('resolution', 'Resolution'),
    ]
    
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='updates')
    update_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='note')
    update_text = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='complaint_updates')
    internal_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Attachments for updates
    attachment = models.FileField(upload_to='updates/attachments/%Y/%m/%d/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Send email notification for status updates
        if self.update_type == 'status_update' and self.complaint.email:
            self.complaint.send_status_update_email(self.update_text, 
                self.updated_by.username if self.updated_by else "System")
    
    def __str__(self):
        return f"{self.update_type} for {self.complaint.complaint_id} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Complaint Update"
        verbose_name_plural = "Complaint Updates"


class AIAnalysisLog(models.Model):
    ANALYSIS_TYPE_CHOICES = [
        ('category', 'Category Classification'),
        ('sentiment', 'Sentiment Analysis'),
        ('priority', 'Priority Prediction'),
        ('urgency', 'Urgency Detection'),
        ('spam', 'Spam Detection'),
        ('summary', 'Text Summarization'),
    ]
    
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='ai_logs')
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPE_CHOICES)
    input_text = models.TextField()
    result = models.JSONField()
    confidence = models.FloatField(default=0.0)
    model_version = models.CharField(max_length=50, default='1.0')
    processing_time = models.FloatField(default=0.0)  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} for {self.complaint.complaint_id} (Confidence: {self.confidence:.2f})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "AI Analysis Log"
        verbose_name_plural = "AI Analysis Logs"