#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')
sys.path.insert(0, os.getcwd())

# Setup Django
django.setup()

# Now create the migrations
from django.core.management import call_command

try:
    # This will run makemigrations and handle prompts
    call_command('makemigrations', verbosity=2)
    print("\n✅ Migrations created successfully")
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
