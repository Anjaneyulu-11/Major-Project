with open('public_pulse/settings.py', 'r') as f: 
    content = f.read() 
 
if 'pulse_admin' not in content: 
    print('Adding pulse_admin to INSTALLED_APPS...') 
    lines = content.split('\n') 
    new_content = [] 
    for line in lines: 
        new_content.append(line) 
        if 'INSTALLED_APPS' in line and '[' in line: 
            new_content.append(\"    'pulse_admin',\") 
    with open('public_pulse/settings.py', 'w') as f2: 
        f2.write('\n'.join(new_content)) 
    print('û Added pulse_admin to INSTALLED_APPS') 
else: 
    print('pulse_admin already in INSTALLED_APPS') 
