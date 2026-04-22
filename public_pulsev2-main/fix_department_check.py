import sys 
f = open('public_pulse/landing_page/views.py', 'r') 
lines = f.readlines() 
f.close() 
ECHO is on.
# We need to comment out the entire department check block 
# Lines 313-324 
for i in range(313, 325):  # Python is 0-indexed, adjust for actual lines 
        lines[i] = '# ' + lines[i] 
ECHO is on.
f = open('public_pulse/landing_page/views.py', 'w') 
f.writelines(lines) 
f.close() 
print('Commented out department check block') 
