import sys 
f = open('public_pulse/landing_page/views.py', 'r') 
content = f.read() 
f.close() 
ECHO is on.
print('Searching for login.html references...') 
lines = content.split('\n') 
for i, line in enumerate(lines): 
    if 'login.html' in line.lower(): 
        print(f'Line {i+1}: {line.strip()}') 
