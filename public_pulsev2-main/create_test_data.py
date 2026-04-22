# create_test_data.py - Creates test complaints for admin dashboard
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')

import django
django.setup()

from django.db.models import Count
from complaints.models import Complaint
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta

def create_test_complaints():
    """Create test complaint data for admin dashboard"""
    
    print("=" * 60)
    print("CREATING TEST COMPLAINTS FOR ADMIN DASHBOARD")
    print("=" * 60)
    
    # Get or create a test user
    try:
        user = User.objects.get(username='testcitizen')
        print("✓ Using existing test user: testcitizen")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testcitizen',
            email='citizen@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Citizen'
        )
        print("✓ Created new test user: testcitizen")
    
    # Sample data
    categories = ['Roads & Infrastructure', 'Electricity', 'Water Supply', 
                  'Sanitation & Waste', 'Healthcare', 'Education', 
                  'Public Transport', 'Internet Service', 'Property Tax']
    
    statuses = ['Submitted', 'In Progress', 'Resolved', 'Closed']
    
    priorities = ['High', 'Medium', 'Low']
    
    cities = ['Hyderabad', 'Secunderabad', 'Madhapur', 'Gachibowli', 
              'Hitech City', 'Banjara Hills', 'Jubilee Hills']
    
    departments = ['Roads Department', 'Electricity Board', 'Water Works', 
                   'Health Department', 'Education Dept', 'Municipal Corp']
    
    # Check existing complaints
    existing = Complaint.objects.count()
    if existing > 0:
        print(f"\n⚠️  Found {existing} existing complaints.")
        choice = input("Delete existing complaints? (y/n): ").lower()
        if choice == 'y':
            Complaint.objects.all().delete()
            print("✓ Deleted all existing complaints.")
    
    # Create 25 test complaints
    print(f"\nCreating test complaints...")
    for i in range(1, 26):
        # Random dates within last 30 days
        days_ago = random.randint(0, 30)
        created_date = datetime.now() - timedelta(days=days_ago)
        
        # Determine status for realistic dates
        status = random.choice(statuses)
        
        complaint = Complaint(
            user=user,
            name=f'Citizen User {i}',
            email=f'citizen{i}@example.com',
            phone=f'98{random.randint(10000000, 99999999)}',
            address=f'{random.randint(1, 100)} Main Street, Area {random.randint(1, 10)}',
            category=random.choice(categories),
            sub_category=random.choice(['Repair', 'New Connection', 'Billing Issue', 
                                        'Quality Problem', 'Maintenance', 'Installation']),
            details=f"""Complaint #{i}: Issue with {random.choice(categories)}.
        
Problem Description: {random.choice([
    'Potholes on main road causing accidents',
    'Power outage for more than 12 hours',
    'Water contamination in pipeline',
    'Garbage not collected for 3 days',
    'Street lights not working',
    'Drainage blockage causing water logging'
])}

Location: Near {random.choice(['school', 'hospital', 'market', 'park', 'residential complex'])}
Date of Issue: {(created_date - timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d')}
Impact: Affecting approximately {random.randint(50, 500)} residents

Request: Please resolve this issue urgently."""
,
            city=random.choice(cities),
            pincode=f'500{random.randint(100, 999)}',
            status=status,
            ai_priority=random.choice(priorities),
            ai_sentiment=random.choice(['Negative', 'Very Negative', 'Neutral', 'Positive']),
            ai_confidence=f'{random.randint(75, 95)}%',
            assigned_to=random.choice(departments + [None]),
            resolution_details=random.choice([
                'Issue resolved. Team visited site and fixed the problem.',
                'Work order has been issued to contractor.',
                'Forwarded to concerned department for action.',
                'Under investigation by field team.',
                'Waiting for budget approval.',
                ''
            ]) if status in ['Resolved', 'Closed'] else '',
        )
        
        # Save first to generate IDs
        complaint.save()
        
        # Update timestamps for realistic data
        complaint.created_at = created_date
        
        if status in ['Resolved', 'Closed']:
            # Resolved some days after submission
            resolved_days = random.randint(1, 10)
            complaint.updated_at = created_date + timedelta(days=resolved_days)
        else:
            complaint.updated_at = created_date + timedelta(days=random.randint(0, 3))
        
        complaint.save()
        
        # Progress indicator
        if i % 5 == 0:
            print(f"  Created {i}/25 complaints...")
    
    print("✓ Created 25 test complaints!")
    
    # Create some urgent high-priority complaints
    print("\nCreating urgent high-priority complaints...")
    urgent_categories = ['Electricity', 'Water Supply', 'Healthcare']
    
    for j in range(1, 6):
        complaint = Complaint(
            user=user,
            name=f'Urgent Citizen {j}',
            email=f'urgent{j}@example.com',
            phone=f'99{random.randint(10000000, 99999999)}',
            address=f'Urgent Location {j}, Emergency Zone',
            category=random.choice(urgent_categories),
            details=f"""🚨 URGENT COMPLAINT #{j}
            
Emergency: {random.choice([
    'Power outage in hospital area - life support systems affected',
    'Water pipeline burst - flooding in residential area',
    'Medical emergency - ambulance service not available',
    'Fire hazard - electrical short circuit in building',
    'Gas leak - dangerous situation in apartment complex'
])}

Immediate action required! Lives at risk.""",
            city='Hyderabad',
            pincode='500001',
            status='Submitted',
            ai_priority='High',
            ai_sentiment='Very Negative',
            ai_confidence='98%',
        )
        complaint.save()
        print(f"  Created URGENT complaint: {complaint.display_id}")
    
    # Show final statistics
    print("\n" + "=" * 60)
    print("📊 DATABASE STATISTICS")
    print("=" * 60)
    
    total = Complaint.objects.count()
    print(f"Total Complaints: {total}")
    
    # Status breakdown
    print("\n📈 By Status:")
    status_counts = Complaint.objects.values('status').annotate(count=Count('id')).order_by('status')
    for stat in status_counts:
        print(f"  {stat['status']}: {stat['count']}")
    
    # Priority breakdown
    print("\n🚨 By Priority:")
    priority_counts = Complaint.objects.values('ai_priority').annotate(count=Count('id')).order_by('ai_priority')
    for pri in priority_counts:
        print(f"  {pri['ai_priority']}: {pri['count']}")
    
    # Category breakdown
    print("\n📁 Top Categories:")
    category_counts = Complaint.objects.values('category').annotate(count=Count('id')).order_by('-count')[:5]
    for cat in category_counts:
        print(f"  {cat['category']}: {cat['count']}")
    
    print("\n" + "=" * 60)
    print("✅ TEST DATA CREATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart your Django server if it's running")
    print("2. Go to admin dashboard: http://127.0.0.1:8000/admin/")
    print("3. Login with your admin credentials")
    print("4. You should now see real data in the dashboard!")
    print("\nFor testing login, use:")
    print("  Username: testcitizen")
    print("  Password: testpass123")
    print("=" * 60)

if __name__ == '__main__':
    create_test_complaints()