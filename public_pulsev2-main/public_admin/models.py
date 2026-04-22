from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
import json

# ========== DEPARTMENT MANAGEMENT MODELS ==========

class Department(models.Model):
    """Departments for complaint assignment and department users"""
    DEPARTMENT_CATEGORIES = [
        ('municipal', 'Municipal Issues'),
        ('electricity', 'Electricity'),
        ('water', 'Water Supply'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('transport', 'Transport'),
        ('corruption', 'Corruption & Bribery'),
        ('safety', 'Public Safety'),
        ('general', 'General Complaint'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, default='')
    category = models.CharField(max_length=20, choices=DEPARTMENT_CATEGORIES, unique=True)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                            limit_choices_to={'is_staff': True})
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure slug is always generated from name when empty
        if not self.slug and self.name:
            base = slugify(self.name)
            slug_candidate = base
            # Ensure uniqueness by appending counter if necessary
            counter = 1
            while Department.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{base}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)
    
    def get_complaints_count(self):
        """Get number of complaints assigned to this department"""
        from complaints.models import Complaint as CitizenComplaint
        return CitizenComplaint.objects.filter(department_category=self.category).count()

class DepartmentUser(models.Model):
    """Users who belong to specific departments"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='department_profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=50, default='Officer', help_text="Role in department")
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True)
    can_assign = models.BooleanField(default=False, help_text="Can assign complaints to others")
    can_resolve = models.BooleanField(default=True, help_text="Can resolve complaints")
    can_escalate = models.BooleanField(default=False, help_text="Can escalate complaints")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['department__name', 'user__username']
        verbose_name = 'Department User'
        verbose_name_plural = 'Department Users'
    
    def __str__(self):
        return f"{self.user.username} - {self.department.name}"

# ========== ADMIN MANAGEMENT MODELS ==========

class Category(models.Model):
    """Complaint categories for better organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    color = models.CharField(max_length=7, default='#3b82f6', help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class AdminLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('resolve', 'Resolve'),
        ('assign', 'Assign'),
        ('escalate', 'Escalate'),
        ('export', 'Export'),
        ('bulk', 'Bulk Operation'),
    ]
    
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'
    
    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.model_name}"

class AdminNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_complaint', 'New Complaint'),
        ('new_user', 'New User'),
        ('status_change', 'Status Change'),
        ('system_alert', 'System Alert'),
        ('feedback', 'New Feedback'),
        ('assigned', 'Complaint Assigned'),
        ('high_priority', 'High Priority Alert'),
        ('escalated', 'Complaint Escalated'),
        ('department_assigned', 'Department Assigned'),
    ]
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Admin Notification'
        verbose_name_plural = 'Admin Notifications'
    
    def __str__(self):
        return self.title

class SystemSetting(models.Model):
    SETTING_TYPES = [
        ('general', 'General'),
        ('email', 'Email'),
        ('notification', 'Notification'),
        ('analytics', 'Analytics'),
        ('security', 'Security'),
        ('priority', 'Priority Settings'),
        ('department', 'Department Settings'),
    ]
    
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='general')
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['setting_type', 'name']
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return self.name

# ========== DASHBOARD ANALYTICS MODELS ==========

class DashboardMetric(models.Model):
    """Store calculated metrics for dashboard performance"""
    METRIC_TYPES = [
        ('total_complaints', 'Total Complaints'),
        ('resolved_today', 'Resolved Today'),
        ('pending_complaints', 'Pending Complaints'),
        ('user_satisfaction', 'User Satisfaction Score'),
        ('high_priority_count', 'High Priority Complaints'),
        ('department_resolved', 'Department Resolved'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.FloatField(default=0)
    date = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', 'metric_type']
        verbose_name = 'Dashboard Metric'
        verbose_name_plural = 'Dashboard Metrics'
        unique_together = ['metric_type', 'date', 'department']
    
    def __str__(self):
        dept_name = self.department.name if self.department else 'System'
        return f"{self.get_metric_type_display()} - {dept_name} - {self.date}"

class QuickAction(models.Model):
    """Predefined quick actions for admin dashboard"""
    ACTION_TYPES = [
        ('resolve', 'Mark as Resolved'),
        ('assign', 'Assign to Department'),
        ('escalate', 'Escalate Priority'),
        ('follow_up', 'Schedule Follow-up'),
        ('export', 'Export Data'),
        ('message', 'Message User'),
        ('view_details', 'View Details'),
        ('reassign', 'Reassign Complaint'),
    ]
    
    name = models.CharField(max_length=100)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    description = models.TextField()
    shortcut_key = models.CharField(max_length=10, blank=True, help_text="Keyboard shortcut")
    user_type = models.CharField(max_length=20, choices=[
        ('admin', 'Administrator'),
        ('department', 'Department'),
        ('both', 'Both')
    ], default='admin')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Quick Action'
        verbose_name_plural = 'Quick Actions'
    
    def __str__(self):
        return self.name

# ========== HELPER FUNCTIONS ==========

def log_admin_action(admin, action, model_name, object_id, description, request=None):
    """Helper function to log admin actions"""
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    AdminLog.objects.create(
        admin=admin,
        action=action,
        model_name=model_name,
        object_id=str(object_id),
        description=description,
        ip_address=ip_address
    )

def create_admin_notification(notification_type, title, message, user=None, department=None):
    """Helper function to create admin notifications"""
    AdminNotification.objects.create(
        notification_type=notification_type,
        title=title,
        message=message,
        user=user,
        department=department
    )

def get_dashboard_metrics(user=None, department=None):
    """Calculate real-time dashboard metrics"""
    today = timezone.now().date()
    
    # Import here to avoid circular import
    from complaints.models import Complaint as CitizenComplaint
    
    metrics = {}
    
    # Base queryset
    complaints = CitizenComplaint.objects.all()
    
    # Filter by department if specified
    if department and isinstance(department, Department):
        complaints = complaints.filter(department_category=department.category)
    
    # Total complaints
    metrics['total_complaints'] = complaints.count()
    
    # Resolved today
    metrics['resolved_today'] = complaints.filter(
        status='Resolved',
        updated_at__date=today
    ).count()
    
    # Pending complaints
    metrics['pending_complaints'] = complaints.filter(
        status__in=['Submitted', 'In Progress']
    ).count()
    
    # User satisfaction (placeholder)
    metrics['user_satisfaction'] = 4.2
    
    # High priority complaints
    metrics['high_priority_count'] = complaints.filter(
        ai_priority__in=['High'],
        status__in=['Submitted', 'In Progress']
    ).count()
    
    # Save to DashboardMetric for historical tracking
    for metric_type, value in metrics.items():
        DashboardMetric.objects.update_or_create(
            metric_type=metric_type,
            date=today,
            department=department,
            defaults={'value': value}
        )
    
    return metrics

def is_department_user(user):
    """Check if user is a department user"""
    return hasattr(user, 'department_profile')

def get_user_department(user):
    """Get department for a user"""
    try:
        return DepartmentUser.objects.get(user=user).department
    except DepartmentUser.DoesNotExist:
        return None

# REMOVED THE AUTO-RUNNING create_default_departments() CALL AT MODULE LEVEL
# This will be called manually or through a management command

def create_default_departments():
    """Create default departments if they don't exist"""
    print("Creating default departments...")
    for category_id, category_name in Department.DEPARTMENT_CATEGORIES:
        try:
            dept, created = Department.objects.get_or_create(
                category=category_id,
                defaults={
                    'name': category_name,
                    'description': f'Handles {category_name.lower()} complaints'
                }
            )
            if created:
                print(f"Created department: {category_name}")
            else:
                print(f"Department already exists: {category_name}")
        except Exception as e:
            print(f"Error creating department {category_name}: {e}")