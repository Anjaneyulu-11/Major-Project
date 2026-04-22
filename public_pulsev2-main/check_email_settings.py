import sys 
sys.path.append('.') 
from public_pulse import settings 
 
print("="*50) 
print("EMAIL SETTINGS CHECK") 
print("="*50) 
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}") 
print(f"EMAIL_HOST_PASSWORD: {'[SET]' if settings.EMAIL_HOST_PASSWORD else '[NOT SET]'}") 
print(f"EMAIL_HOST: {settings.EMAIL_HOST}") 
print(f"EMAIL_PORT: {settings.EMAIL_PORT}") 
