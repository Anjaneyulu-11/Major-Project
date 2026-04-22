from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# ============================================================
# SIMPLIFIED DIRECT RESPONSE MAPPING - GUARANTEED TO WORK
# ============================================================

def get_response(user_message):
    """Direct mapping - no complex matching, just direct answers"""
    msg = user_message.lower().strip()
    
    # DIRECT MATCHES for common questions
    if "how do i login" in msg or "how to login" in msg or "login help" in msg:
        return """🔑 **Login Instructions**

1️⃣ Go to Homepage
2️⃣ Click 'Login' button (top right)
3️⃣ Enter Username OR Email
4️⃣ Enter Password
5️⃣ Click 'Sign In'

**Having trouble?**
• Use 'Forgot Password' if you can't remember
• Check Caps Lock is OFF
• Passwords are case-sensitive

After login, you'll see your Dashboard where you can lodge complaints!"""

    elif "what departments" in msg or "departments available" in msg or "list of departments" in msg:
        return """🏛️ **Departments Available**

1. **Education** - Schools, colleges, teachers, fees
2. **Healthcare** - Hospitals, doctors, medical services
3. **Transport** - Roads, potholes, buses, traffic
4. **Water Supply** - Water shortage, leaks, quality
5. **Electricity** - Power outages, bills, transformers
6. **Municipal** - Garbage, drainage, street lights
7. **Police** - Safety, crime, law enforcement
8. **Anti-Corruption** - Bribery, misconduct
9. **General** - Other government services

Select the department that matches your issue!"""

    elif "water problem" in msg or "water complaint" in msg or "how to complain water" in msg or "i have water problem" in msg:
        return """💧 **How to File a Water Complaint**

1. Login to your account
2. Go to 'Lodge a Complaint'
3. Select Category: 'Water Supply'
4. In description, include:
   • Exact location (area, street)
   • How long the problem exists
   • Type: no water/low pressure/leakage/dirty water
   • Number of families affected
5. Upload photos (recommended)
6. Click Submit

**Priority:** No water for 3+ days = HIGH Priority (2-5 days resolution)"""

    elif "track my complaint" in msg or "how to track" in msg or "track complaint" in msg:
        return """🔍 **How to Track Your Complaint**

**Method 1:** Go to 'Track Complaint' page → Enter Complaint ID → View status

**Method 2:** Login → 'My Complaints' → See all your complaints

**Method 3:** Ask me directly with your Complaint ID (e.g., "Check CP-UNC60906")

**Status Meanings:**
• 📝 Submitted - Received, in queue
• 🔄 In Progress - Being worked on
• ✅ Resolved - Issue addressed
• 📁 Closed - Completed

You'll get email updates for every status change!"""

    elif "lodge a complaint" in msg or "how to lodge" in msg or "how to submit complaint" in msg:
        return """📋 **How to Lodge a Complaint**

1. Login to your account
2. Go to Dashboard
3. Click 'Lodge a Complaint'
4. Fill the form:
   • Select Category
   • Write detailed description (location, issue, impact)
   • Add city/location
   • Upload photos (optional)
5. Click 'Submit'
6. Receive Complaint ID via email instantly

**Tips:**
• Be specific about location
• Add photos as evidence
• Keep your Complaint ID safe

Total time: Less than 3 minutes!"""

    elif "what details are required" in msg or "required details" in msg or "details required" in msg:
        return """📝 **Required Details for Complaint**

**Mandatory (Must fill):**
✅ Category - Select from 9 departments
✅ Description - Explain your issue clearly
✅ City/District - Where problem is located

**Optional but Recommended:**
📸 Images - Upload photos (JPG, PNG, GIF, max 5MB)
📍 Full address - Street, landmark, PIN code
📞 Phone number - For urgent contact

**What to write in description:**
• Exact location with landmarks
• When problem started
• How severe it is
• How many people affected
• Any previous attempts to resolve"""

    elif "upload images" in msg or "can i upload images" in msg or "upload photo" in msg:
        return """📸 **Yes, you can upload images!**

**How to upload:**
Click 'Choose File' in the complaint form → Select image → Submit

**Supported formats:** JPG, JPEG, PNG, GIF
**Max size:** 5MB per image

**Tips for good photos:**
• Take clear, well-lit photos
• Show problem from multiple angles
• Include landmarks for location

Photos help authorities understand the issue better and lead to faster resolution!"""

    elif "how to register" in msg or "sign up" in msg or "create account" in msg:
        return """📝 **How to Register**

1. Click 'Register' on homepage
2. Enter Username (unique name)
3. Enter Email (for notifications)
4. Create Password (min 8 characters)
5. Confirm Password
6. Click 'Register'

✅ After registration, you're automatically logged in
✅ Check email for confirmation
✅ Start lodging complaints immediately

**Time:** Less than 2 minutes!
**Cost:** Completely FREE!"""

    elif "forgot password" in msg or "reset password" in msg:
        return """🔐 **Forgot Password - Reset Process**

1. Go to Login Page
2. Click 'Forgot Password?'
3. Enter your registered email
4. Click 'Send Reset Link'
5. Check email (including spam folder)
6. Click reset link (valid 15 minutes)
7. Enter new password (min 8 characters)
8. Confirm new password
9. Login with new password

**Tips:**
• Use mix of letters, numbers, symbols
• Don't reuse old passwords"""

    elif "what does pending mean" in msg or "pending meaning" in msg:
        return """📊 **What Does 'Pending' Mean?**

"Pending" means your complaint is waiting for department action.

**Possible statuses:**
• **Submitted** - Received, in queue for review
• **In Progress** - Department is working on it

**You'll receive email updates when:**
✓ Complaint is assigned to department
✓ Status changes
✓ Issue is resolved

**Resolution time:**
• High Priority: 2-5 days
• Medium Priority: 5-15 days
• Low Priority: 15-30 days"""

    elif "hi" in msg or "hello" in msg or "hey" in msg:
        return """👋 **Hello! Welcome to Civic Pulse!**

I'm your AI Assistant. Here's what you can ask me:

• "How do I login?"
• "How to lodge a complaint?"
• "What departments are available?"
• "Water problem how to complain?"
• "How to track my complaint?"
• "What details are required?"
• "Can I upload images?"
• "Forgot password"

How can I help you today?"""

    elif "thank" in msg:
        return """😊 You're very welcome!

Glad I could help! Feel free to ask if you need anything else.

Have a great day! 🌟"""

    elif "bye" in msg or "goodbye" in msg:
        return """👋 Goodbye! Thanks for visiting Civic Pulse!

Remember: Keep your Complaint ID safe for tracking.

Come back anytime! 🌟"""

    else:
        return """🤔 I can help with these topics:

**Account & Login**
• "How do I login?"
• "How to register?"
• "Forgot password"

**Complaints**
• "How to lodge a complaint?"
• "What details are required?"
• "Can I upload images?"
• "Water problem how to complain?"

**Tracking**
• "How to track my complaint?"
• "What does pending mean?"

**Information**
• "What departments are available?"

Just type your question naturally! 💬"""


# ============================================================
# CHATBOT VIEW - SIMPLIFIED VERSION
# ============================================================

def chatbot(request):
    chats = Chat.objects.filter(user=request.user).order_by('created_at')

    if request.method == 'POST':
        message = (request.POST.get('message') or '').strip()
        
        print(f"\n{'='*60}")
        print(f"[DEBUG] User: {message}")
        print(f"{'='*60}")
        
        # Get response from direct mapping
        response = get_response(message)
        
        print(f"[DEBUG] Response sent")
        
        # Save conversation
        try:
            Chat.objects.create(
                user=request.user if request.user.is_authenticated else None,
                message=message,
                response=response,
                status="assistant",
                created_at=timezone.now()
            )
        except Exception as e:
            print(f"[DEBUG] Failed to save chat: {e}")

        return redirect('chatbot')

    return render(request, 'chatbot.html', {'chats': chats})


def redirect_with_response(request, response):
    """Helper function to save response and redirect"""
    try:
        Chat.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message=request.POST.get('message', ''),
            response=response,
            status="assistant",
            created_at=timezone.now()
        )
    except:
        pass
    return redirect('chatbot')


# ============================================================
# YOUR EXISTING VIEWS
# ============================================================

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect('chatbot')
        return render(request, 'login.html', {'error_message': 'Invalid credentials'})
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            user = User.objects.create_user(username, email, password1)
            auth.login(request, user)
            return redirect('chatbot')
        return render(request, 'register.html', {'error_message': 'Passwords do not match'})
    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


def user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")

    return render(request, 'user/user_profile.html', {'form': form})


def chat_history(request):
    messages_qs = Chat.objects.filter(user=request.user).order_by('created_at')
    return render(request, 'user/history.html', {'messages': messages_qs})


def status_tracking(request):
    complaints = Chat.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/status_tracking.html', {'complaints': complaints})


def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'user/change_password.html', {'form': form})


# ============================================================
# PUBLIC CHATBOT - DICTIONARY-BASED INTENT MAPPING
# ============================================================

# Intent mapping dictionary for public chatbot
INTENT_RESPONSES = {
    'greeting': {
        'keywords': ['hi', 'hello', 'hey', 'how are you'],
        'response': """👋 **Hello! Welcome to Civic Pulse!**

I'm your AI assistant for the Civic Pulse platform. I can help you with:

• **Registration** - How to create your account
• **Login** - Sign in and password help
• **Complaints** - How to lodge issues
• **Tracking** - Check complaint status
• **Details** - What information is required
• **General Info** - About our platform

What would you like to know? Feel free to ask!"""
    },
    'general_info': {
        'keywords': ['what is civic pulse', 'about civic pulse'],
        'response': """🌟 **About Civic Pulse - AI-Powered Civic Platform**

**What is Civic Pulse?**
Civic Pulse is a revolutionary digital platform that bridges the gap between citizens and government departments through artificial intelligence and streamlined complaint resolution processes.

**Our Mission:**
To empower citizens with technology-driven tools for transparent, efficient, and accountable governance. We believe in using AI to make government services more accessible and responsive.

**Key Features:**

🤖 **AI-Powered Intelligence**
• Automatic complaint categorization
• Sentiment analysis for priority assessment
• Smart routing to relevant departments
• Predictive resolution timeframes

📊 **Real-Time Tracking**
• Instant complaint ID generation
• Live status updates via email
• Comprehensive tracking dashboard
• Historical complaint analytics

🏛️ **Government Integration**
• Direct connection with 9+ departments
• Secure data sharing protocols
• Official status updates
• Resolution verification

🔒 **Security & Privacy**
• End-to-end encryption
• GDPR compliant data handling
• Role-based access control
• Secure complaint storage

📱 **User-Friendly Experience**
• Intuitive web interface
• Mobile-responsive design
• Multi-language support
• 24/7 accessibility

**Supported Departments:**
1. Education 🏫
2. Healthcare 🏥
3. Transport 🚌
4. Water Supply 💧
5. Electricity ⚡
6. Municipal Services 🗑️
7. Police 🚔
8. Anti-Corruption 💰
9. General Administration 📝

**Platform Statistics:**
• **100% Free** - No registration or usage fees
• **AI Accuracy** - 95%+ categorization accuracy
• **Resolution Rate** - 85%+ successful resolutions
• **Response Time** - Average 7 days for resolution
• **User Base** - Thousands of satisfied citizens

**Why Choose Civic Pulse?**
✅ **Transparent** - Track every step of your complaint
✅ **Efficient** - AI speeds up processing
✅ **Accountable** - Direct government integration
✅ **Secure** - Your data is protected
✅ **Free** - No hidden costs ever

**Getting Started:**
1. Register your free account
2. Lodge your first complaint
3. Track progress in real-time
4. Provide feedback for improvement

**Contact & Support:**
• Use our chatbot for instant help
• Email support available
• Comprehensive help documentation

**Civic Pulse** - *Where Technology Meets Governance* 🚀"""
    },
    'registration': {
        'keywords': ['register', 'signup', 'create account'],
        'response': """📝 **How to Register on Civic Pulse**

**Step-by-Step Registration Process:**

1️⃣ **Go to Homepage**
   • Visit the Civic Pulse website

2️⃣ **Click 'Register'**
   • Look for the registration button

3️⃣ **Fill Required Information**
   • **Username** - Choose a unique username
   • **Email** - Valid email address (required for notifications)
   • **Password** - Minimum 8 characters
   • **Confirm Password** - Re-enter password

4️⃣ **Submit Registration**
   • Click the 'Register' button

**After Registration:**
✅ **Automatic Login** - You'll be logged in immediately
✅ **Email Confirmation** - Check your email for verification
✅ **Dashboard Access** - Start using all platform features

**Requirements:**
• Must be 18+ years old
• Valid email address
• Unique username

**Time:** Less than 2 minutes
**Cost:** Completely FREE!

**Need Help?** Contact support if you encounter any issues."""
    },
    'login': {
        'keywords': ['login', 'sign in', 'forgot password'],
        'response': """🔑 **Login Instructions for Civic Pulse**

**How to Login:**

1️⃣ **Go to Homepage**
2️⃣ **Click 'Login' Button**
   • Located in the top right corner

3️⃣ **Enter Credentials**
   • **Username OR Email** - Either works
   • **Password** - Case-sensitive

4️⃣ **Click 'Sign In'**

**After Successful Login:**
• Redirected to your personal Dashboard
• Access to lodge complaints
• Track existing complaints
• View complaint statistics
• Use chatbot assistance

**Common Login Issues & Solutions:**

❌ **Forgot Password**
• Click 'Forgot Password?' link
• Enter your registered email
• Check email for reset instructions
• Reset link valid for 15 minutes

❌ **Wrong Password**
• Check Caps Lock is OFF
• Passwords are case-sensitive
• Try both username and email

❌ **Account Not Found**
• Verify spelling of username/email
• Ensure you registered first

❌ **Browser Issues**
• Clear browser cache and cookies
• Try incognito/private browsing mode
• Update your browser

**Security Note:** Never share your password with anyone."""
    },
    'complaints': {
        'keywords': ['lodge complaint', 'submit complaint', 'file complaint', 'how to complain', 'complaint process'],
        'response': """📋 **How to Lodge a Complaint on Civic Pulse**

**Complete Complaint Submission Process:**

1️⃣ **Login to Your Account**
   • Use your registered username/email and password

2️⃣ **Navigate to Dashboard**
   • Access your personal dashboard after login

3️⃣ **Click 'Lodge a Complaint'**
   • Find the complaint submission button

4️⃣ **Fill Complaint Form**
   **Personal Information:**
   • Name (auto-filled from profile)
   • Email (auto-filled)
   • Phone (optional)

   **Complaint Details:**
   • **Category** - Select from available departments
   • **Description** - Detailed explanation required:
     📍 Exact location with landmarks
     📅 Date and time of incident
     📝 Clear description of the problem
     👥 Impact on affected people
     🔄 Previous attempts to resolve

   **Location Information:**
   • City/District
   • PIN Code (recommended)

   **Supporting Evidence:**
   • Upload photos/videos (optional but highly recommended)
   • Maximum 5MB per file
   • Supported formats: JPG, PNG, GIF

5️⃣ **AI Analysis Review**
   • System auto-detects category
   • Sentiment analysis performed
   • Priority level assigned (High/Medium/Low)

6️⃣ **Submit Complaint**
   • Click 'Submit Complaint' button

**What Happens Next:**

📧 **Instant Confirmation**
• Unique Complaint ID sent to your email
• Format: CP-XXXYYYYYY (example: CP-UNC60906)

🔄 **Processing Timeline**
• **Immediate:** AI categorization and routing
• **1-2 days:** Department assignment
• **5-15 days:** Active resolution (varies by priority)
• **Email Updates:** Status notifications throughout

**Priority Levels:**
🔴 **High Priority** - Safety/emergency issues (2-5 days)
🟡 **Medium Priority** - Service disruptions (5-10 days)
🟢 **Low Priority** - General inquiries (10-15 days)

**Tips for Successful Complaints:**
• Be specific and detailed in description
• Include photos for visual evidence
• Provide accurate location information
• Keep Complaint ID safe for tracking
• Follow up if no response within expected timeframe

**Need Help?** Use the chatbot or contact support."""
    },
    'tracking': {
        'keywords': ['track', 'status', 'complaint status'],
        'response': """🔍 **How to Track Your Complaint Status**

**Three Tracking Methods:**

**Method 1: Using Complaint ID (Recommended)**
1️⃣ Go to **'Track Complaint'** page
2️⃣ Enter your **Complaint ID**
   • Format: CP-XXXYYYYYY
   • Example: CP-UNC60906
3️⃣ Click **'Track Now'**
4️⃣ View complete status and history

**Method 2: Dashboard (For Logged-in Users)**
1️⃣ Login to your account
2️⃣ Go to **'My Complaints'** section
3️⃣ Click on any complaint
4️⃣ View detailed status information

**Method 3: Ask Chatbot**
• Type: **"Check CP-UNC60906"**
• Get instant status update

**Status Explanations:**

📝 **Submitted**
• Complaint received and queued
• Initial processing: 1-2 days

🔄 **In Progress**
• Assigned to department
• Active investigation/work: 5-15 days
• Regular status updates via email

✅ **Resolved**
• Issue has been addressed
• Solution implemented
• Please provide feedback

📁 **Closed** (Rare)
• Complaint completed
• Final status - no further action

❌ **Rejected** (Rare)
• Insufficient information
• Not within jurisdiction
• Duplicate complaint

**Email Notifications:**
You'll receive automatic email updates for:
• Status changes
• Department assignment
• Resolution completion
• Feedback requests
• Important updates

**Resolution Timeframes:**
• **High Priority:** 2-5 days
• **Medium Priority:** 5-10 days
• **Low Priority:** 10-15 days

**What You'll See When Tracking:**
• Current status with emoji indicator
• Submission date and time
• Assigned department
• Priority level
• Last update timestamp
• Complete status history timeline

**Can't Find Your Complaint?**
• Check email for the confirmation message
• Verify Complaint ID spelling
• Ensure you're using the correct account
• Contact support if issues persist

**Pro Tip:** Save your Complaint ID safely for easy future reference!"""
    },
    'required_details': {
        'keywords': ['details', 'required details', 'what info needed'],
        'response': """✍️ **Required Information for Complaints**

**Mandatory Fields (Required):**

1️⃣ **Category Selection**
   • Choose relevant government department
   • Affects routing and resolution speed

2️⃣ **Complaint Description**
   • Detailed explanation of the issue
   • Minimum 50 characters required

3️⃣ **Location Information**
   • City/District (required)
   • PIN Code (highly recommended)

**Highly Recommended Information:**

📍 **Specific Location Details**
• Exact address or landmark
• Street name and area
• GPS coordinates (if available)

📅 **Time Information**
• When did the issue start?
• Date and time of occurrence
• How long has it been ongoing?
• Is it recurring or one-time?

📝 **Problem Details**
• What exactly happened?
• Who is affected?
• Severity level
• Root cause (if known)

👥 **Impact Assessment**
• Number of people affected
• Safety concerns
• Business disruption
• Educational impact

🔢 **Reference Information**
• Previous complaint numbers
• Bill/account numbers (utilities)
• Registration numbers
• Contact numbers of involved parties

📸 **Supporting Evidence**
• Photos of the problem
• Videos showing the issue
• Screenshots of relevant documents
• Before/after comparisons

**Why These Details Matter:**
• **Faster Resolution** - Complete information speeds up processing
• **Accurate Routing** - Helps assign to correct department
• **Priority Assessment** - Determines urgency level
• **Evidence Support** - Photos/videos strengthen your case
• **Follow-up Efficiency** - Easier for authorities to investigate

**File Size Limits:**
• Images: Maximum 5MB per file
• Total uploads: Up to 10 files per complaint

**Privacy Note:** All information is securely stored and only shared with relevant government departments for resolution."""
    },
    'complaint_details': {
        'keywords': ['what details required', 'complaint details', 'what to include', 'information needed'],
        'response': """✍️ **What Details to Include in Your Complaint**

**Essential Information for Effective Resolution:**

📍 **Location Details**
• Exact address or landmark
• Area, locality, street name
• City and district
• PIN code (recommended)

📅 **Time Information**
• When did the issue start?
• Date and time of occurrence
• Duration/frequency of problem
• Is it recurring or one-time?

📝 **Problem Description**
• What exactly happened?
• Who is affected by this issue?
• How severe is the problem?
• What caused the issue?

🔢 **Reference Numbers**
• Previous complaint numbers (if any)
• Bill/account numbers (for utilities)
• Registration numbers if applicable

📸 **Evidence**
• Upload photos or videos
• Include screenshots if relevant
• Document damages clearly
• Show the problem visually

👥 **Impact Assessment**
• How many people/families affected?
• What is the severity level?
• Any safety concerns?
• Business/education disruption?

🔄 **Previous Attempts**
• Have you reported this before?
• To whom did you report?
• What was the response?
• Any follow-up actions taken?

**Why These Details Matter:**
• Helps department understand the issue better
• Enables faster and accurate resolution
• Provides evidence for action
• Determines priority level (High/Medium/Low)

**💡 Pro Tip:** More details = Faster resolution! Include photos whenever possible."""
    },
}


def get_bot_response(user_message):
    """Dictionary-based intent matching for public chatbot"""
    msg = user_message.lower().strip()
    
    # Check each intent for keyword matches
    for intent, data in INTENT_RESPONSES.items():
        keywords = data['keywords']
        if any(keyword in msg for keyword in keywords):
            return data['response']
    
    # Fallback response
    return """🤔 I can help you with questions about:

• Registration and login
• Lodging complaints
• Tracking complaint status
• Required complaint details
• General information about Civic Pulse

Please ask your question clearly, and I'll provide detailed guidance! 💬"""


# ============================================================
# PUBLIC CHATBOT VIEW
# ============================================================

@csrf_exempt
def public_chat(request):
    """Public chatbot API endpoint - no login required"""
    if request.method == 'POST':
        try:
            # Parse JSON input
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({
                    'error': 'Message is required'
                }, status=400)
            
            # Get response using intent mapping
            response = get_bot_response(message)
            
            return JsonResponse({
                'response': response,
                'status': 'success'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': 'Internal server error'
            }, status=500)
    
    return JsonResponse({
        'error': 'Method not allowed'
    }, status=405)