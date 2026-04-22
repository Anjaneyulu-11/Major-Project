import uuid
import datetime
import random
import string
from django.db import models
from django.contrib.auth.models import User
from public_admin.models import Department

class Complaint(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]
    
    SENTIMENT_CHOICES = [
        ('Very Negative', 'Very Negative'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
        ('Positive', 'Positive'),
        ('Very Positive', 'Very Positive'),
    ]
    
    # ✅ CRITICAL: Keep complaint_id for admin views
    complaint_id = models.CharField(max_length=36, unique=True, editable=False, blank=True, null=True)
    
    # Additional ID fields
    uuid_id = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    tracking_id = models.CharField(max_length=50, unique=True, editable=False, blank=True, null=True)
    readable_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # User info
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Complaint details
    category = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    sub_category = models.CharField(max_length=100, blank=True, null=True)
    details = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    image = models.ImageField(upload_to='complaint_images/', blank=True, null=True)
    
    # AI Analysis fields
    ai_category = models.CharField(max_length=100, blank=True, null=True)
    ai_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, blank=True, null=True)
    ai_sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, blank=True, null=True)
    ai_confidence = models.CharField(max_length=10, blank=True, null=True)
    
    # Status fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Submitted')
    assigned_to = models.CharField(max_length=100, blank=True, null=True)
    resolution_details = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.readable_id or self.complaint_id} - {self.category}"
    
    def save(self, *args, **kwargs):
        # Check if this is an update and status has changed
        status_changed = False
        old_status = None
        
        if self.pk:  # This is an update (existing complaint)
            try:
                old_instance = Complaint.objects.get(pk=self.pk)
                old_status = old_instance.status
                # Check if status actually changed
                if old_status != self.status:
                    status_changed = True
            except Complaint.DoesNotExist:
                pass
        
        # ✅ Generate complaint_id (MUST EXIST for admin views)
        if not self.complaint_id:
            date_part = datetime.datetime.now().strftime("%Y%m%d")
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.complaint_id = f"CP-{date_part}-{random_part}"
        
        # Generate readable_id
        if not self.readable_id:
            random_chars = ''.join(random.choices(string.ascii_uppercase, k=3))
            random_nums = ''.join(random.choices(string.digits, k=5))
            self.readable_id = f"CP-{random_chars}{random_nums}"
            
            # Ensure uniqueness
            while Complaint.objects.filter(readable_id=self.readable_id).exclude(id=self.id).exists():
                random_chars = ''.join(random.choices(string.ascii_uppercase, k=3))
                random_nums = ''.join(random.choices(string.digits, k=5))
                self.readable_id = f"CP-{random_chars}{random_nums}"
        
        # Generate tracking_id
        if not self.tracking_id:
            date_part = datetime.datetime.now().strftime("%Y%m%d")
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            self.tracking_id = f"TRK-{date_part}-{random_part}"
        
        super().save(*args, **kwargs)
        
        # Create notification if status changed
        # Only notify citizen users (not admin/staff)
        if status_changed and self.user and not self.user.is_staff:
            self._create_status_change_notification()
    
    def _create_status_change_notification(self):
        """Create a notification when complaint status changes"""
        status_messages = {
            'Submitted': f"Your complaint {self.display_id} has been submitted successfully.",
            'In Progress': f"Your complaint {self.display_id} is now being processed.",
            'Resolved': f"Your complaint {self.display_id} has been resolved.",
            'Closed': f"Your complaint {self.display_id} has been closed.",
        }
        
        message = status_messages.get(
            self.status,
            f"Your complaint {self.display_id} status has been updated to {self.status}."
        )
        
        # Create notification (using get_or_create to avoid duplicates)
        # Check if a notification already exists for this status+complaint combination in the last minute
        from django.utils import timezone
        from datetime import timedelta
        recent_threshold = timezone.now() - timedelta(minutes=1)
        
        existing = Notification.objects.filter(
            user=self.user,
            complaint=self,
            message=message,
            created_at__gte=recent_threshold
        ).exists()
        
        if not existing:
            Notification.objects.create(
                user=self.user,
                complaint=self,
                message=message
            )
    
    def get_email_friendly_id(self):
        """Get the ID to display in emails"""
        return self.readable_id or self.complaint_id
    
    def get_tracking_url(self):
        """Generate tracking URL"""
        return f"/complaints/track/?id={self.readable_id or self.complaint_id}"
    
    @property
    def display_id(self):
        """Display ID for templates"""
        return self.readable_id or self.complaint_id
    
    @property
    def short_id(self):
        """Short version of ID"""
        id_str = self.readable_id or self.complaint_id
        if id_str and id_str.startswith('CP-'):
            return id_str[3:]
        return id_str
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'


class Feedback(models.Model):
    """Citizen feedback for complaints"""
    SATISFACTION_CHOICES = [
        (1, 'Very Dissatisfied'),
        (2, 'Dissatisfied'),
        (3, 'Neutral'),
        (4, 'Satisfied'),
        (5, 'Very Satisfied'),
    ]
    
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=SATISFACTION_CHOICES)
    comment = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
    
    def __str__(self):
        return f"Feedback for {self.complaint.display_id}: {self.rating}/5"


class Notification(models.Model):
    """
    In-app notifications for citizens when their complaint status changes.
    Created automatically when complaint status changes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.complaint.display_id}"
