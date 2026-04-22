# Department Login Testing Guide

## Quick Verification Steps

### 1. Verify No More AttributeError
Run this command to confirm the application loads without the previous error:
```bash
python manage.py check
# Expected output: System check identified no issues (0 silenced)
```

### 2. Test URL Patterns
Verify that the broken URL patterns are removed:
```bash
python manage.py show_urls | grep department
# Should show only:
# department/dashboard/   landing_page.views.department_dashboard
```

### 3. Run Development Server
```bash
python manage.py runserver
# Application should start without errors
# Visit: http://localhost:8000/login/
```

## Manual Testing Workflow

### Test 1: Department Login Flow (Same Page)
1. **Navigate to Login Page**: `http://localhost:8000/login/`
2. **Observe Initial State**:
   - Should see three role buttons: Citizen, Admin, Department
   - Username/Password fields visible
   - Citizen role selected by default
   - No department selection visible

3. **Click Department Button**:
   - Department card should become highlighted
   - Department selection grid should appear below
   - Captcha verification section should appear

4. **Select Department**:
   - Click any department card (e.g., "Municipal Issues")
   - Card should highlight with blue border
   - Department slug should be stored in hidden input

5. **Enter Credentials**:
   - Username: `department123`
   - Password: `department123`
   - Captcha Answer: Enter the sum of the two displayed numbers

6. **Submit Login**:
   - Click "Sign In" button
   - Should redirect to `/department/dashboard/`
   - Should see success message

### Test 2: Department Dashboard
1. **Verify Header**: Should show "XYZ Department Dashboard"
2. **Verify Statistics Cards**:
   - Total Complaints: Should show count
   - Pending: Should show count
   - In Progress: Should show count
   - Resolved: Should show count

3. **Verify Complaints Table**:
   - Headers: #ID, Title, Status, Created, Action
   - Each row should show complaint data
   - Status badges should be color-coded

4. **Test Status Update**:
   - Click status dropdown on any complaint
   - Select new status (e.g., "In Progress")
   - Should see success message
   - Table should refresh with updated status

### Test 3: Captcha Validation
1. **Navigate to Login**: `/login/`
2. **Select Department Role**
3. **Select Any Department**
4. **Enter Wrong Captcha**: Enter incorrect number
5. **Submit Form**: Should see error "Invalid captcha answer"
6. **Verify Captcha Re-renders**: Same numbers should display again

### Test 4: Department Selection Validation
1. **Navigate to Login**: `/login/`
2. **Select Department Role**
3. **Do NOT select a department**
4. **Try to Submit**: Should see error "Please select a department"
5. **Select Department**: Error should clear
6. **Try Again**: Should proceed with validation

### Test 5: Citizen Login (Existing Flow)
1. **Navigate to Login**: `/login/`
2. **Keep Citizen Role Selected** (default)
3. **Enter Valid Credentials**: Existing citizen user
4. **No Department Selection**: Should not appear
5. **No Captcha**: Should not appear
6. **Submit**: Should redirect to `/dashboard/citizen/`

### Test 6: Admin Login (Existing Flow)
1. **Navigate to Login**: `/login/`
2. **Click Admin Button**
3. **Enter Admin Credentials**: Admin user
4. **No Department Selection**: Should not appear
5. **Submit**: Should redirect to `/pulse_admin/`

### Test 7: Session Variables
After successful department login, verify session contains:
```python
# In Django shell or debug toolbar:
request.session.get('department_logged_in')  # True
request.session.get('department_slug')       # 'municipal-issues' (example)
request.session.get('department_id')         # 1 (example)
request.session.get('department_name')       # 'Municipal Issues' (example)
```

### Test 8: Logout
1. **From Department Dashboard**: Click "Logout" button
2. **Should be redirected**: `/`
3. **Session should be cleared**: No department_* keys in session
4. **Try accessing /department/dashboard/**: Should redirect to `/login/`

## Expected Behavior

### Department Login Success Path
```
/login/ (Department role selected)
  ↓
Department selection visible + Captcha displayed
  ↓
User selects department and enters captcha
  ↓
POST to /login/ with: user_type=department, department=slug, captcha=answer
  ↓
Validate department selection ✓
Validate captcha (a + b = answer) ✓
Authenticate user ✓
  ↓
Store in session: department_slug, department_id, department_name
  ↓
Redirect to /department/dashboard/
  ↓
Display filtered complaints for that department
```

### Error Scenarios
1. **No Department Selected**: 
   - Error message: "Please select a department"
   - Page re-renders with department grid

2. **Wrong Captcha**:
   - Error message: "Invalid captcha answer"
   - Captcha values regenerated (new numbers shown)

3. **Invalid Credentials**:
   - Error message: "Invalid department credentials"
   - Page re-renders with department grid

4. **Unauthorized Department**:
   - Error message: "You are not authorized for this department"
   - User redirected to login

## Files Changed

| File | Changes |
|------|---------|
| `public_pulse/landing_page/urls.py` | ✅ Removed broken department/select/* and department/login/ patterns |
| `public_pulse/landing_page/views.py` | ✅ Rewrote user_login() with department logic; Fixed department_dashboard() |
| `templates/landing_page/login.html` | ✅ Added department grid, captcha fields, JavaScript handlers |
| `templates/landing_page/department_dashboard.html` | ✅ Created new template with statistics and complaints table |

## Troubleshooting

### Issue: "AttributeError: module 'public_pulse.landing_page.views' has no attribute 'select_department'"
- **Solution**: This error should be fixed. Run `python manage.py check` to verify.

### Issue: Department grid not showing after clicking Department button
- **Cause**: JavaScript not executing
- **Solution**: Check browser console for errors; verify no JS syntax errors in login.html

### Issue: Captcha always shows "Invalid captcha answer"
- **Cause**: Session values not being stored/retrieved correctly
- **Solution**: Check Django settings for SESSION_ENGINE configuration

### Issue: Complaint table showing 0 results
- **Cause**: No complaints exist with department FK
- **Solution**: Create test complaints with department field set

## Integration with Existing System

✅ **Citizen Login**: Unchanged, still works as before
✅ **Admin Login**: Unchanged, still works as before  
✅ **Session Storage**: Uses Django session framework (configurable)
✅ **Database**: Reads departments from Department model
✅ **Complaints**: Filters by department FK
✅ **Authentication**: Optional - supports both real users and dev credentials
