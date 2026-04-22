f=open('public_pulse/landing_page/views.py','r') 
c=f.read() 
f.close() 
l=c.split(chr(10))   # chr(10) is newline
for i in range(313,324): 
        if not l[i].strip().startswith('#'): 
            l[i]='# '+l[i] 
n=chr(10).join(l) 
f=open('public_pulse/landing_page/views.py','w') 
f.write(n) 
f.close() 
print('Fixed lines 314-324') 
