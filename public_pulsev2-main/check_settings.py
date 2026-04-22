with open('public_pulse/settings.py', 'r') as f: 
    content = f.read() 
 
if 'pulse_admin' in content: 
    print('û pulse_admin is in INSTALLED_APPS') 
else: 
    print('? pulse_admin is NOT in INSTALLED_APPS') 
