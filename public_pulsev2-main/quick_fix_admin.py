import re 
with open('templates/pulse_admin/user_management.html', 'r', encoding='utf-8', errors='ignore') as f: 
   text = f.read() 
with open('templates/pulse_admin/user_management.html', 'w', encoding='utf-8') as f: 
   f.write(text) 
print('Fixed all map filters') 
