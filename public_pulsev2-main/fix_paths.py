# -*- coding: utf-8 -*- 
import re 
 
# Read the file 
with open('public_pulse/landing_page/views.py', 'r', encoding='utf-8', errors='ignore') as f: 
    text = f.read() 
 
# Replace template paths 
text = text.replace("'landing_page/auc/login.html'", "'landing_page/login.html'") 
text = text.replace('"landing_page/auc/login.html"', '"landing_page/login.html"') 
text = text.replace('auc/login.html', 'login.html') 
 
# Write back 
with open('public_pulse/landing_page/views.py', 'w', encoding='utf-8') as f: 
    f.write(text) 
 
print('û STEP 1: Fixed template paths in views.py') 
