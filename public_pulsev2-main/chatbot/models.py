from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Chat(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('resolved', 'Resolved'),
        ('pending', 'Pending'),
    )
    CATEGORY_CHOICES = [
        ('Transport', 'Transport'),
        ('Education', 'Education'),
        ('Security', 'Security'),
        ('Public Service', 'Public Service'),
        ('Sanitation', 'Sanitation'),
        ('Environment', 'Environment'),
        ('Health', 'Health'),
        ('Services', 'Services'),
        ('Housing', 'Housing'),
        ('Infrastructure', 'Infrastructure'),
        ('Jobs', 'Jobs'),
        ('Sports', 'Sports')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    response = models.TextField(default="I am sorry. I don't understand your question")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    classification = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username}:{self.message}:{self.sentiment_score}:{self.created_at}:{self.category}'

    def sentiment_status(self):
        if self.sentiment_score is not None:
            if self.sentiment_score > 0.1:
                return "Positive"
            elif self.sentiment_score < -0.1:
                return "Negative"
            else:
                return "Neutral"
        return "Unknown"


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say'),
    ]
    
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('department_staff', 'Department Staff'),
        ('department_head', 'Department Head'),
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=100)
    
    # Role field
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='citizen')

    # Contact Information
    phone = models.CharField(max_length=15, blank=True, null=True)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)

    # Location
    address = models.TextField(blank=True, null=True)
    sub_county = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    # Personal Details
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)

    # Profile Media
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    whatsapp_notifications = models.BooleanField(default=False)

    # Statistics
    total_complaints = models.IntegerField(default=0)
    pending_complaints = models.IntegerField(default=0)
    resolved_complaints = models.IntegerField(default=0)
    rejected_complaints = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Auto-set full_name
        if not self.full_name and self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"

        # Auto-set email from user if not set
        if self.user and not self.email:
            self.email = self.user.email

        # Don't calculate statistics on every save - use update_statistics() method instead
        # This prevents circular imports and improves performance

        super().save(*args, **kwargs)

    def update_statistics(self):
        """Update complaint statistics for this user profile"""
        if self.user and self.user.pk:
            # Use apps.get_model to avoid circular imports
            from django.apps import apps
            try:
                Complaint = apps.get_model('landing_page', 'Complaint')
                # Get all complaints by this user
                complaints = Complaint.objects.filter(user=self.user)
                
                # Update counts
                self.total_complaints = complaints.count()
                self.pending_complaints = complaints.filter(status='Pending').count()
                self.resolved_complaints = complaints.filter(status='Resolved').count()
                self.rejected_complaints = complaints.filter(status='Rejected').count()
                
                # Calculate average rating from complaints with ratings
                rated_complaints = complaints.filter(citizen_rating__isnull=False)
                if rated_complaints.exists():
                    avg = rated_complaints.aggregate(
                        models.Avg('citizen_rating')
                    )['citizen_rating__avg']
                    self.average_rating = round(float(avg or 0), 1)
                else:
                    self.average_rating = 0.0
                
                # Save only the statistics fields
                self.save(update_fields=[
                    'total_complaints',
                    'pending_complaints', 
                    'resolved_complaints',
                    'rejected_complaints',
                    'average_rating',
                    'updated_at'
                ])
                return True
            except Exception as e:
                # Silently fail if Complaint model doesn't exist yet
                print(f"Error updating statistics: {e}")
                return False

    @property
    def display_name(self):
        return self.full_name or f"{self.first_name} {self.last_name}"
    
    @property
    def is_staff_member(self):
        return self.role in ['department_staff', 'department_head', 'admin', 'moderator']
    
    @property
    def is_citizen(self):
        return self.role == 'citizen'

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name or '',
            last_name=instance.last_name or '',
            email=instance.email
        )
        # Update statistics after creating profile
        profile.update_statistics()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name or '',
            last_name=instance.last_name or '',
            email=instance.email
        )
        # Update statistics after creating profile
        profile.update_statistics()