import re 
 
with open('pulse_admin/views.py', 'r', encoding='utf-8') as f: 
    content = f.read() 
 
# Replace all pulse_admin/ template paths with admin/pulse_admin/ 
content = content.replace("render(request, 'pulse_admin/", "render(request, 'admin/pulse_admin/") 
 
with open('pulse_admin/views.py', 'w', encoding='utf-8') as f: 
    f.write(content) 
 
print("Fixed template paths in views.py") 
print("Changed: pulse_admin/  admin/pulse_admin/") 
