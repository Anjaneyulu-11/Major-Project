import re 
with open('templates/pulse_admin/user_management.html', 'r', encoding='utf-8', errors='ignore') as f: 
    content = f.read() 
ECHO is on.
# Remove ALL map filters 
ECHO is on.
with open('templates/pulse_admin/user_management.html', 'w', encoding='utf-8') as f: 
    f.write(content) 
ECHO is on.
print('Fixed all map and sum filters') 
