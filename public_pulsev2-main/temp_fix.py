import sys 
f = open('public_pulse/landing_page/views.py', 'r') 
lines = f.readlines() 
f.close() 
for i in range(len(lines)): 
    if 'dept_user = DepartmentUser.objects.get(user=user)' in lines[i]: 
        print('Found line', i+1) 
        lines[i] = '# ' + lines[i] 
f = open('public_pulse/landing_page/views.py', 'w') 
f.writelines(lines) 
f.close() 
print('Fixed') 
