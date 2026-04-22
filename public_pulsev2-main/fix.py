print("Fixing login template path...") 
with open('public_pulse/landing_page/views.py', 'r') as f: 
    content = f.read() 
print("Replacing auc/login.html with login.html...") 
new_content = content.replace("'landing_page/auc/login.html'", "'landing_page/login.html'") 
new_content = new_content.replace('"landing_page/auc/login.html"', '"landing_page/login.html"') 
new_content = new_content.replace("auc/login.html", "login.html") 
with open('public_pulse/landing_page/views.py', 'w') as f: 
    f.write(new_content) 
print("Done!") 
