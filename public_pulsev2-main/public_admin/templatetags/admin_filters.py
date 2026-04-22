from django import template

register = template.Library()

@register.filter
def get_resolved_count(user):
    """Get resolved complaints count for a user"""
    try:
        return user.admin_complaints.filter(status='Resolved').count()
    except:
        return 0