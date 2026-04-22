# pulse_admin/admin.py - FIXED VERSION
from django.contrib import admin
from .models import (
    Department, DepartmentUser, AdminLog, AdminNotification, SystemSetting,
    DashboardMetric, QuickAction
    # AlertRule and SavedReport removed as they don't exist
)

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ['admin', 'action', 'model_name', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['admin__username', 'description']

@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'setting_type', 'is_active']
    list_filter = ['setting_type', 'is_active']
    search_fields = ['name', 'key']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'slug', 'category']

@admin.register(DepartmentUser)
class DepartmentUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'role', 'is_active']
    list_filter = ['department', 'role', 'is_active']
    search_fields = ['user__username', 'department__name', 'role']

@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'value', 'date', 'calculated_at']
    list_filter = ['metric_type', 'date']
    readonly_fields = ['calculated_at']

@admin.register(QuickAction)
class QuickActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'action_type', 'is_active', 'order']
    list_filter = ['action_type', 'is_active']

# Note: AlertRule and SavedReport admin classes removed as models don't exist

# Optional: Register your Complaint model from complaints app
from complaints.models import Complaint
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['display_id', 'name', 'category', 'status', 'ai_priority', 'created_at']
    list_filter = ['status', 'ai_priority', 'category']
    search_fields = ['complaint_id', 'name', 'email', 'details']
    readonly_fields = ['complaint_id', 'readable_id', 'tracking_id', 'created_at', 'updated_at']
    ordering = ['-created_at']