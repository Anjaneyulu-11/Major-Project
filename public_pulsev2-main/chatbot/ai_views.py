from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
from .models import Chat
from django.utils import timezone
from public_pulse.landing_page.ai_utils import categorize_complaint, analyze_sentiment, detect_priority

# ============================================================
# FULL FAQ KNOWLEDGE BASE - SAME AS YOUR VIEWS.PY
# ============================================================

FAQ_KB = [
    # ==================== 1. BASIC PLATFORM INTRODUCTION ====================
    {
        "keywords": ["what is civic pulse", "about civic pulse", "tell me about civic pulse", "what is this platform", "platform info", "civic pulse platform", "introduction", "what do you do", "platform overview", "explain civic pulse", "what is civic pulse about", "civic pulse meaning", "define civic pulse", "civic pulse kya hai", "what is this website", "purpose of civic pulse", "what does civic pulse do", "civic pulse explained", "tell me about your platform", "what is your platform", "introduce civic pulse", "platform introduction", "civic pulse details", "about your project", "what have you built", "project explanation", "what is this system", "platform description"],
        "answer": "🌟 **Civic Pulse - Smart Civic Engagement Platform**\n\nCivic Pulse is an AI-powered digital platform that revolutionizes how citizens interact with government departments for grievance redressal.\n\n**Core Features:**\n🤖 AI-powered complaint categorization\n😊 Real-time sentiment analysis\n🔍 Unique complaint tracking ID\n📧 Instant email notifications\n👥 Three-tier system (Citizen, Admin, Department)\n📊 Analytics dashboard\n💬 24/7 AI chatbot assistant\n\n**Mission:** Bridge the gap between citizens and government through transparent, efficient, and technology-driven complaint resolution.\n\n**Impact:** Faster resolution times, better accountability, and improved public services for all citizens!"
    },
    
    # ==================== 2. HOW IT WORKS ====================
    {
        "keywords": ["how it works", "how does it work", "working process", "how to use", "platform working", "explain working", "working mechanism", "how does civic pulse work", "process flow", "workflow", "how it functions", "working principle", "system working", "how to operate", "how to use platform", "working steps", "process explained", "how does this work", "tell me how it works", "working methodology", "functional flow", "how to use civic pulse", "platform usage", "how to navigate", "using the platform", "how civic pulse works", "tell me how civic pulse works"],
        "answer": "⚙️ **How Civic Pulse Works - 6 Simple Steps**\n\n**Step 1: Register/Login** 📝\nCreate your free account with email and password\n\n**Step 2: Submit Complaint** 📋\n• Select category (Education, Healthcare, etc.)\n• Describe your issue with location\n• Upload supporting images (optional)\n• AI analyzes in real-time\n\n**Step 3: AI Processing** 🤖\n• Auto-categorizes complaint\n• Detects sentiment (positive/negative/neutral)\n• Assigns priority (High/Medium/Low)\n• 89.2% accuracy rate\n\n**Step 4: Get Complaint ID** 🆔\n• Unique ID sent to your email instantly\n• Format: CP-XXXYYYYYY (e.g., CP-UNC60906)\n• Use ID for tracking\n\n**Step 5: Department Action** 🏛️\n• Complaint routed to relevant department\n• Status updates: Submitted → In Progress → Resolved\n• Email notifications for each update\n\n**Step 6: Track & Feedback** 📊\n• Track anytime using Complaint ID\n• Provide feedback after resolution\n• Help improve services!\n\n**Total time:** Registration <2 min | Complaint submission <3 min | Tracking instant!"
    },
    
    # ==================== 3. REGISTRATION DETAILS ====================
    {
        "keywords": ["how to register", "sign up", "create account", "registration process", "how do i register", "new account", "register", "signup", "create profile", "account creation", "become a user", "join civic pulse", "get started", "create new account", "registration steps", "how to sign up", "account registration", "user registration", "register now", "sign up process", "create login", "make account", "how to become a member", "registration guide", "register on civic pulse", "how to create account", "new user registration", "account setup", "profile creation", "join platform", "become citizen", "registration help", "sign up help", "how can i register", "register procedure", "registration instructions", "create new user", "add account", "setup account", "registration page", "sign up page"],
        "answer": "📝 **Registration Process - Quick & Free!**\n\n**Step-by-Step Guide:**\n\n1️⃣ **Click 'Register'** on the homepage\n2️⃣ **Enter Username** - Choose a unique name (will be visible)\n3️⃣ **Provide Email** - Valid email for notifications and complaint ID\n4️⃣ **Create Password** - Use strong password (min 8 characters)\n5️⃣ **Confirm Password** - Re-enter to verify\n6️⃣ **Click 'Register'** - Submit the form\n\n✅ **After Registration:**\n• You'll be automatically logged in\n• Check email for confirmation\n• Start lodging complaints immediately\n\n**Requirements:**\n• Must be 18+ years\n• Valid email address\n• Phone number optional\n\n**⏱️ Time:** Less than 2 minutes!\n\n**💡 Tip:** Keep your email accessible - all complaint updates go there!"
    },
    
    # ==================== 4. LOGIN QUESTIONS ====================
    {
        "keywords": ["how to login", "sign in", "login process", "how do i login", "login help", "can't login", "login issues", "login not working", "sign in problem", "access account", "enter account", "login page", "sign in page", "login credentials", "username login", "email login", "login with email", "login with username", "how to sign in", "login steps", "login procedure", "access my account", "logging in", "login failed", "login error", "authentication", "user login", "account access", "sign in help", "login troubleshooting", "can't access account", "login not accepting", "wrong password login", "how do i login to civic pulse", "login to my account", "how to sign into civic pulse"],
        "answer": "🔑 **Login Instructions**\n\n**How to Login:**\n\n1️⃣ Go to **Homepage**\n2️⃣ Click **'Login'** button (top right)\n3️⃣ Enter **Username OR Email**\n4️⃣ Enter **Password**\n5️⃣ Click **'Sign In'**\n\n**Login Options:**\n• Use your registered username\n• OR use your email address\n• Both work the same way\n\n**Common Login Issues & Solutions:**\n\n❌ **Wrong Password**\n→ Use 'Forgot Password' to reset\n\n❌ **Account Not Found**\n→ Check if you registered first\n→ Try both username and email\n\n❌ **Caps Lock On**\n→ Passwords are case-sensitive\n\n❌ **Browser Issues**\n→ Clear cache and cookies\n→ Try incognito/private mode\n→ Update browser\n\n**After Successful Login:**\nYou'll be redirected to your **Dashboard** where you can:\n• Lodge new complaints\n• Track existing complaints\n• View complaint statistics\n• Access profile settings\n• Use chatbot for help"
    },
    
    # ==================== 5. COMPLAINT SUBMISSION ====================
    {
        "keywords": ["how to submit complaint", "lodge complaint", "file complaint", "submit complaint", "how to lodge", "complaint submission", "submit issue", "report problem", "how to report", "file grievance", "register complaint", "post complaint", "add complaint", "create complaint", "new complaint", "raise complaint", "submit grievance", "how to file complaint", "complaint filing", "report issue", "how to report issue", "complaint registration", "lodging process", "submit my complaint", "how do I complain", "complaint procedure", "complaint steps", "filing process", "raise issue", "report a problem", "submit a ticket", "create ticket", "open complaint", "start complaint", "begin complaint", "complaint form", "how to use complaint form", "complaint submission steps", "how to lodge a complaint", "how can i lodge a complaint", "how do i lodge a complaint"],
        "answer": "📋 **How to Submit a Complaint - Complete Guide**\n\n**Step-by-Step Process:**\n\n**1. Login to Your Account** 🔐\n• Use username or email\n• Enter your password\n\n**2. Go to Dashboard** 🏠\n• After login, you'll see your dashboard\n• Click **'Lodge a Complaint'** button\n\n**3. Fill Complaint Form** 📝\n\n**Personal Information:**\n• Name (auto-filled from profile)\n• Email (auto-filled)\n• Phone (optional)\n• Address (optional)\n\n**Complaint Details:**\n• **Category** - Select from 8 options\n• **Description** - Be detailed and specific\n  - Include exact location with landmarks\n  - Mention date and time of occurrence\n  - Describe what happened clearly\n  - List any previous attempts to resolve\n  - State expected resolution\n\n**Location Details:**\n• City/District (required)\n• PIN Code (optional but recommended)\n• Address details\n\n**Images (Optional but Recommended):**\n• Upload photos as evidence\n• Supported: JPG, PNG, GIF\n• Max size: 5MB per image\n• Helps authorities understand better\n\n**4. Review AI Analysis** 🤖\n• See auto-detected category\n• Check sentiment analysis\n• Verify priority level\n• AI confidence score\n• Override if needed\n\n**5. Submit** ✅\n• Click **'Submit Complaint'** button\n• Receive unique Complaint ID via email instantly\n• ID format: CP-XXXYYYYYY\n\n**What Happens Next:**\n📧 Email with Complaint ID arrives within 1-2 minutes\n🔍 Track progress using ID\n📊 Status updates sent via email\n✅ Resolution notification when complete\n\n**Tips for Better Resolution:**\n• Be specific about location\n• Add photos for evidence\n• Describe impact clearly\n• Keep Complaint ID safe"
    },
    
    # ==================== 6. COMPLAINT TRACKING ====================
    {
        "keywords": ["how to track complaint", "track complaint", "check status", "complaint status", "tracking process", "status check", "track my complaint", "complaint tracking", "where is my complaint", "complaint progress", "status update", "check my complaint", "track complaint status", "how to check status", "complaint follow up", "tracking help", "status tracking", "complaint location", "find complaint", "check progress", "monitor complaint", "tracking instructions", "status information", "how to track my complaint", "complaint status check", "track complaint id", "status using id", "track by id", "how can i track my complaint", "track my complaint status"],
        "answer": "🔍 **How to Track Your Complaint**\n\n**Three Easy Ways to Track:**\n\n**Method 1: Using Complaint ID** 🆔\n1. Go to **'Track Complaint'** page\n2. Enter your **Complaint ID** (format: CP-XXXYYYYYY)\n3. Click **'Track Now'**\n4. View complete status and timeline\n\n**Method 2: From Dashboard** 📊\n1. Login to your account\n2. Go to **'My Complaints'** section\n3. Click on any complaint to see details\n4. Status displayed prominently\n\n**Method 3: Ask Chatbot** 💬\nSimply type or say: **\"Check CP-UNC60906\"**\nI'll show you the current status instantly!\n\n**What You'll See:**\n📝 **Current Status** - Submitted/In Progress/Resolved/Closed\n📅 **Submission Date** - When complaint was filed\n📍 **Location** - Where issue was reported\n🏛️ **Department** - Who is handling it\n📊 **Priority** - High/Medium/Low\n📈 **Timeline** - Status change history\n\n**Status Meanings:**\n• **Submitted** - Received, in queue\n• **In Progress** - Being worked on\n• **Resolved** - Issue addressed\n• **Closed** - Completed\n\n**Email Updates:**\nYou'll automatically receive email notifications when:\n✓ Complaint is assigned to department\n✓ Status changes\n✓ Resolution is completed\n✓ Feedback requested\n\n**No ID?** Check your email for the confirmation message or login to see all complaints!"
    },
    
    # ==================== 7. WATER COMPLAINTS ====================
    {
        "keywords": ["water problem", "water complaint", "water supply", "water shortage", "no water", "water leakage", "water quality", "drinking water", "water issue", "how to complain water", "water department", "water problem how to complain", "i have water problem", "water complaint process", "water supply complaint", "water tanker", "water pipeline", "water pressure"],
        "answer": "💧 **How to File a Water Supply Complaint**\n\n**Step-by-Step Process:**\n\n1️⃣ **Login** to your Civic Pulse account\n2️⃣ Go to **'Lodge a Complaint'**\n3️⃣ Select Category: **'Water Supply'**\n4️⃣ In description, include:\n   • Exact location (area, street, house number)\n   • Duration of problem (how many days/weeks)\n   • Type of issue (no water, low pressure, leakage, poor quality)\n   • Number of families affected\n   • Any previous complaints filed\n5️⃣ Upload photos of the issue (recommended)\n6️⃣ Click **Submit**\n\n**Common Water Issues We Handle:**\n• No water supply for days\n• Low water pressure\n• Pipeline leakages\n• Dirty/contaminated water\n• Irregular supply timings\n• Damaged water meters\n\n**Priority Level:**\n🔴 **High Priority** - No water for 3+ days, contamination\n🟡 **Medium Priority** - Low pressure, irregular supply\n🟢 **Low Priority** - Minor leakages, general complaints\n\n**Expected Resolution Time:**\n• High Priority: 2-5 days\n• Medium Priority: 5-10 days\n• Low Priority: 10-15 days\n\n**💡 Tip:** Be specific about your location and include photos of the issue for faster resolution!"
    },
    
    # ==================== 8. WHAT DETAILS ARE REQUIRED ====================
    {
        "keywords": ["what details are required", "required details", "details needed", "what information needed", "complaint details required", "what to fill", "form details", "required information", "what details to provide", "what do i need to submit", "complaint requirements", "mandatory fields", "compulsory details", "what should i provide"],
        "answer": "📝 **Required Details for Submitting a Complaint**\n\n**Mandatory Fields (Must Fill):**\n✅ **Category** - Select from 8 options (Education, Healthcare, Water, Electricity, Transport, Municipal, Public Safety, Corruption)\n✅ **Description** - Detailed explanation of your issue\n✅ **City/District** - Where the problem is located\n\n**Optional but Recommended:**\n📸 **Images** - Upload photos as evidence (JPG, PNG, GIF, max 5MB)\n📍 **Full Address** - Street name, landmark, PIN code\n📞 **Phone Number** - For urgent contact if needed\n\n**What to Include in Description:**\n• Exact location with landmarks\n• When the problem started\n• How severe the issue is\n• How many people are affected\n• Any previous attempts to resolve\n• What resolution you expect\n\n**Example of Good Description:**\n\"For the past 2 weeks, there is no water supply in Rajiv Nagar, Sector 12. We are 50+ families affected. The water pipeline on Main Road has been leaking since last month. We've called the municipal office 5 times but no action. Please fix immediately.\"\n\n**💡 Tip:** The more details you provide, the faster your complaint gets resolved!"
    },
    
    # ==================== 9. IMAGE UPLOAD ====================
    {
        "keywords": ["upload images", "upload photo", "attach image", "add picture", "photo evidence", "upload images with complaint", "can i upload images", "image upload", "photo upload", "attach photos", "add photos", "can i upload photos", "images with complaint", "photo attachment", "picture upload"],
        "answer": "📸 **Yes, you can upload images with your complaint!**\n\n**How to Upload:**\n1️⃣ In the complaint form, click **'Choose File'** button\n2️⃣ Select image from your device\n3️⃣ Image will appear as selected\n4️⃣ Submit your complaint\n\n**Supported Formats:**\n✅ JPG / JPEG\n✅ PNG\n✅ GIF\n\n**File Size Limits:**\n📏 Maximum: **5MB per image**\n📏 If larger, compress before uploading\n\n**Tips for Good Photos:**\n• Take clear, well-lit photos\n• Capture the problem from multiple angles\n• Include landmarks for location reference\n• Show scale (use object for size reference)\n• Take close-ups for details\n\n**What to Photograph:**\n📸 Water leakage - Show source and damage\n📸 Potholes - Show depth and location\n📸 Garbage - Show extent and location\n📸 Road damage - Show area and surroundings\n\n**Important Notes:**\n⚠️ No videos supported (use images)\n⚠️ Multiple images allowed\n⚠️ Images are stored securely\n⚠️ Only you and department can view\n\n**💡 Tip:** Photos help authorities understand the issue better and lead to faster resolution!"
    },
    
    # ==================== 10. DEPARTMENTS AVAILABLE ====================
    {
        "keywords": ["what departments", "departments available", "available departments", "department list", "list of departments", "which departments", "what departments are available", "departments in civic pulse", "department categories", "government departments", "department details", "department information", "department names", "all departments", "department options", "complaint departments"],
        "answer": "🏛️ **Departments Available in Civic Pulse**\n\n**1. Education Department** 🏫\n• Schools, colleges, universities\n• Teacher conduct, fees, infrastructure\n\n**2. Healthcare Department** 🏥\n• Hospitals, clinics, medical services\n• Doctor conduct, facilities, negligence\n\n**3. Transport Department** 🚌\n• Roads, public transport, traffic\n• Potholes, signals, bus services\n\n**4. Water Supply Department** 💧\n• Water distribution, quality\n• Shortage, leaks, pressure issues\n\n**5. Electricity Department** ⚡\n• Power supply, billing\n• Outages, fluctuations, transformer issues\n\n**6. Municipal Corporation** 🗑️\n• Civic services, sanitation\n• Garbage, drainage, street lights, parks\n\n**7. Police Department** 🚔\n• Public safety, law enforcement\n• Safety concerns, police response, crime\n\n**8. Anti-Corruption Bureau** 💰\n• Corruption, bribery cases\n• Bribery demands, misconduct, fraud\n\n**9. General Administration** 📝\n• Other government services\n• Miscellaneous complaints\n\n**How to Choose:**\nSelect the department that best matches your issue. AI will also auto-detect and suggest the correct category!\n\n**💡 Tip:** Choosing the right department ensures your complaint reaches the right officials faster!"
    },
    
    # ==================== 11. STATUS MEANINGS ====================
    {
        "keywords": ["status meaning", "what does pending mean", "pending meaning", "what does resolved mean", "resolved meaning", "what does in progress mean", "in progress meaning", "submitted meaning", "closed meaning", "complaint status meanings", "status explained", "what means submitted", "status definitions", "pending status", "resolved status"],
        "answer": "📊 **Complaint Status Meanings**\n\n**📝 SUBMITTED**\n• Complaint successfully received\n• In queue for initial review\n• Not yet assigned to department\n• **Next:** In Progress\n\n**🔄 IN PROGRESS**\n• Assigned to relevant department\n• Officials are working on resolution\n• Investigation/action underway\n• **Next:** Resolved or Closed\n\n**✅ RESOLVED**\n• Issue has been addressed\n• Action taken by department\n• Feedback requested via email\n• **Next:** Closed (auto after feedback)\n\n**📁 CLOSED**\n• Complaint fully completed\n• No further action needed\n• Archived in system\n• **Next:** None - final status\n\n**❌ REJECTED**\n• Complaint deemed invalid\n• Insufficient information provided\n• Outside department jurisdiction\n\n**What Does PENDING Mean?**\n\"Pending\" means your complaint is waiting for department action. It's either in **Submitted** or **In Progress** status. You'll receive email updates when the status changes!\n\n**Email Notifications:**\nYou'll receive email alerts for EVERY status change! Check your inbox regularly."
    },
    
    # ==================== 12. FORGOT PASSWORD ====================
    {
        "keywords": ["forgot password", "reset password", "change password", "password reset", "forgot my password", "can't login", "password recovery", "reset my password", "how to reset password", "password help", "forgot login", "lost password", "password change", "i forgot my password"],
        "answer": "🔐 **Forgot Password - Reset Process**\n\n**Step-by-Step:**\n\n1️⃣ Go to **Login Page**\n2️⃣ Click **'Forgot Password?'** link\n3️⃣ Enter your **registered email address**\n4️⃣ Click **'Send Reset Link'**\n5️⃣ Check your email (including spam folder)\n6️⃣ Click the **reset link** (valid for 15 minutes)\n7️⃣ Enter **new password** (min 8 characters)\n8️⃣ Confirm new password\n9️⃣ Click **'Reset Password'**\n🔟 Login with new password\n\n**Important Notes:**\n⏱️ Reset link expires in **15 minutes**\n📧 Check spam folder if email not received\n🔒 New password should be strong and unique\n❌ If multiple attempts fail, contact support\n\n**Password Tips:**\n• Use mix of letters, numbers, symbols\n• Minimum 8 characters\n• Don't use personal information\n• Don't reuse old passwords"
    },
    
    # ==================== 13. DATA SECURITY ====================
    {
        "keywords": ["data secure", "is my data secure", "privacy", "data security", "is data safe", "secure platform", "data protection", "security measures", "safe", "secure", "data privacy", "information security", "personal data", "how secure", "security features", "protection", "confidentiality"],
        "answer": "🔒 **Yes, your data is completely secure!**\n\n**Security Measures in Place:**\n\n**Password Security** 🔐\n• Passwords hashed with PBKDF2\n• 100,000 iterations of SHA-256\n• Never stored in plain text\n\n**Data Encryption** 🔒\n• HTTPS for all communications\n• SSL/TLS encryption\n• Secure data transmission\n\n**Access Control** 👥\n• Role-Based Access Control (RBAC)\n• Citizens see only their complaints\n• Departments see only assigned complaints\n\n**What We DON'T Do:**\n❌ Sell your data to third parties\n❌ Share information without consent\n❌ Store sensitive information unnecessarily\n❌ Use data for marketing\n\n**Your Privacy Rights:**\n✅ You can view all your data\n✅ Request data deletion\n✅ Update profile information\n\n**Compliance:**\n📋 Follows data protection principles\n📋 Regular security audits\n\n**💡 Remember:** Your data is safe with Civic Pulse!"
    },
    
    # ==================== 14. CHATBOT HELP ====================
    {
        "keywords": ["what can chatbot do", "chatbot help", "what can you do", "chatbot capabilities", "chatbot features", "chatbot functions", "what can you help with", "what questions can I ask", "chatbot assistance", "chatbot services", "chatbot abilities", "chatbot skills", "what can I ask", "chatbot purpose", "chatbot role", "how to use chatbot", "chatbot usage", "using chatbot", "chatbot instructions", "chatbot guide", "chatbot commands", "what to ask chatbot", "chatbot options", "chatbot menu", "chatbot support", "assistant capabilities"],
        "answer": "💬 **What I Can Help You With**\n\n**I'm your AI Assistant - Ask me anything about Civic Pulse!**\n\n**📝 Registration & Account:**\n• How to register\n• Login issues\n• Forgot password\n• Profile updates\n\n**📋 Complaint Submission:**\n• How to lodge a complaint\n• What categories exist\n• What details are required\n• Can I upload images\n• Water problem complaints\n\n**🔍 Complaint Tracking:**\n• How to track my complaint\n• Status meanings\n• Where to find complaint ID\n\n**🏛️ Platform Features:**\n• What departments are available\n• How Civic Pulse works\n• Is my data secure\n\n**❓ General Questions:**\n• Platform purpose\n• Free to use\n• Contact support\n\n**How to Use Me:**\n• Type your question naturally\n• Ask follow-up questions\n• I remember conversation context\n\n**Try These Examples:**\n• \"How do I register?\"\n• \"How to lodge a complaint?\"\n• \"What departments are available?\"\n• \"I have a water problem, how to complain?\"\n• \"How can I track my complaint?\"\n• \"What details are required?\"\n\n**I'm here 24/7 to help!** 🌟"
    },
    
    # ==================== 15. GREETINGS ====================
    {
        "keywords": ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "namaste", "hola", "howdy", "what's up", "hi there", "hello there", "hey there", "greeting"],
        "answer": "👋 **Hello! Welcome to Civic Pulse!**\n\nI'm your AI Assistant, here to help you with everything about the platform.\n\n**Quick Start:**\n• **New user?** Ask me \"How to register\"\n• **Need to complain?** Ask \"How to lodge a complaint\"\n• **Water problem?** Ask \"How to complain about water\"\n• **Track complaint?** Ask with your Complaint ID\n• **Departments?** Ask \"What departments are available\"\n\n**I can help with:**\n📝 Registration & Login\n📋 Submitting complaints\n🔍 Tracking status\n🔒 Security & privacy\n🏛️ Department info\n\n**Try asking me anything!** How can I assist you today? 🌟"
    },
    
    # ==================== 16. THANK YOU ====================
    {
        "keywords": ["thank you", "thanks", "thx", "thankyou", "appreciate it", "much appreciated", "thank you so much", "thanks a lot", "thanks for help", "grateful", "thankful", "thnx", "ty", "tysm"],
        "answer": "😊 **You're very welcome!**\n\nI'm glad I could help you today. That's what I'm here for!\n\n**Remember:**\n• Keep your Complaint ID safe\n• Track status anytime\n• Provide feedback after resolution\n• I'm here 24/7 if you need more help\n\n**Is there anything else I can help you with?** Feel free to ask more questions or explore the platform!\n\nHave a great day! 🌟"
    },
    
    # ==================== 17. GOODBYE ====================
    {
        "keywords": ["goodbye", "bye", "see you", "bye bye", "see you later", "take care", "cya", "farewell", "adios", "bye for now", "talk later", "catch you later"],
        "answer": "👋 **Goodbye! Thanks for visiting Civic Pulse!**\n\n**Before you go:**\n✅ Remember your Complaint ID for tracking\n✅ Check email for updates\n✅ Come back anytime to track progress\n✅ I'm always here to help!\n\n**Have a great day!** 🌟\n\nCome back anytime you need help with complaints or have questions. Take care!"
    },
    
    # ==================== 18. IS IT FREE ====================
    {
        "keywords": ["is civic pulse free", "free to use", "cost", "any charges", "paid", "subscription cost", "free platform", "free service", "pay for use", "money", "payment required", "free account", "free registration", "cost to use", "pricing", "fees", "any fees"],
        "answer": "💰 **Completely Free!**\n\n**Yes, Civic Pulse is 100% FREE for all citizens!**\n\n**No Hidden Costs:**\n✅ Free registration\n✅ Free complaint submission\n✅ Free tracking\n✅ Free email notifications\n✅ Free chatbot assistance\n\n**No Subscription Fees:**\n• No monthly charges\n• No annual fees\n• No premium tiers\n\n**What's Free:**\n• Register account\n• Lodge complaints\n• Track status\n• Receive updates\n• Use chatbot\n\n**Forever Free:** Civic Pulse is committed to keeping services free for all citizens.\n\n**Start using Civic Pulse today - no credit card, no payment!** 🌟"
    },
    
    # ==================== 19. CONTACT SUPPORT ====================
    {
        "keywords": ["contact support", "help", "support", "get help", "customer support", "contact us", "need help", "support team", "contact information", "help desk", "reach support", "email support", "support contact", "how to contact", "support email"],
        "answer": "📞 **Contact Support**\n\n**Get Help When You Need It:**\n\n**Email Support** 📧\n• **Address:** civicpulse.govt@gmail.com\n• **Response Time:** 24-48 hours\n\n**Chat Support** 💬\n• **Method:** Use this chatbot!\n• **Response:** Instant\n\n**Contact Form** 📝\n• **Location:** Website footer\n• **Response:** 24-48 hours\n\n**What to Include in Your Message:**\n✅ Your username/email\n✅ Complaint ID (if applicable)\n✅ Detailed description of issue\n✅ Screenshots (if helpful)\n\n**Support Hours:**\n• **Chat:** 24/7 (AI assistant always available)\n• **Email:** Mon-Fri, 9 AM - 6 PM\n\n**Emergency Issues:**\n⚠️ For emergencies requiring immediate response:\n• Police: 100\n• Fire: 101\n• Ambulance: 102\n\n**We're Here to Help!**"
    },
]


def get_best_faq_match(user_message):
    """Simple but effective keyword matching for FAQ"""
    user_message_lower = user_message.lower().strip()
    user_message_clean = re.sub(r'[^\w\s]', '', user_message_lower)
    
    best_match = None
    best_score = 0
    
    # Special case mappings for common queries
    special_cases = {
        "how do i login": "login",
        "how to login": "login",
        "login help": "login",
        "can't login": "login",
        "water problem": "water",
        "water complaint": "water",
        "how to complain water": "water",
        "i have water problem": "water",
        "track my complaint": "track",
        "how to track": "track",
        "track complaint": "track",
        "what departments": "departments",
        "departments available": "departments",
        "list of departments": "departments",
        "what details are required": "details",
        "details required": "details",
        "upload images": "images",
        "can i upload images": "images",
        "upload photo": "images",
        "how to register": "register",
        "registration": "register",
        "sign up": "register",
        "forgot password": "password",
        "reset password": "password",
        "complaint status": "status",
        "what does pending mean": "status",
        "what does resolved mean": "status",
    }
    
    # Check special cases first
    for case_phrase, case_type in special_cases.items():
        if case_phrase in user_message_lower:
            for item in FAQ_KB:
                keywords = item.get("keywords", [])
                if case_type in ' '.join(keywords).lower():
                    return item.get("answer")
    
    # Regular keyword matching
    for item in FAQ_KB:
        keywords = item.get("keywords", [])
        answer = item.get("answer", "")
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            if keyword_lower in user_message_clean:
                score = len(keyword_lower) / max(len(user_message_clean), 1)
                
                if keyword_lower == user_message_clean:
                    score = 1.0
                
                important_keywords = ['login', 'water', 'track', 'department', 'details', 'image', 'register', 'password', 'status']
                if any(imp in keyword_lower for imp in important_keywords):
                    score *= 1.5
                
                if score > best_score:
                    best_score = score
                    best_match = answer
    
    if best_score > 0.15:
        return best_match
    
    return None


@csrf_exempt
def ai_chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            user = request.user
            
            # First try to match from FAQ_KB
            faq_response = get_best_faq_match(message)
            
            if faq_response:
                response = faq_response
                category = "FAQ_Response"
                sentiment_label = "Neutral"
                priority = "Medium"
                sentiment_score = 0.5
            else:
                # Fallback to AI processing
                category = categorize_complaint(message)
                sentiment_label, insight, sentiment_score = analyze_sentiment(message)
                priority = detect_priority(message)
                
                # Generate AI response for unmatched queries
                if any(word in message.lower() for word in ['hello', 'hi', 'hey', 'greetings']):
                    response = "Hello! 👋 I'm your AI Assistant for Civic Pulse. How can I help you with your complaints today?"
                elif any(word in message.lower() for word in ['lodge', 'submit', 'file', 'register']):
                    response = "To lodge a complaint:\n1. Click 'Lodge Complaint' in Quick Actions\n2. Fill in the complaint details\n3. Add location and images if needed\n4. Submit the form\n\nYou'll receive a Complaint ID for tracking."
                elif any(word in message.lower() for word in ['track', 'status', 'check', 'progress']):
                    response = "To track a complaint:\n1. Click 'Track Complaint' in Quick Actions\n2. Enter your Complaint ID\n3. View detailed status and updates\n\nYou can also see recent complaints in your dashboard."
                elif any(word in message.lower() for word in ['category', 'categories', 'type']):
                    response = "Complaint categories include:\n• Municipal Issues (roads, garbage)\n• Electricity\n• Water Supply\n• Healthcare\n• Education\n• Transport\n• Corruption\n• Public Safety\n\nYour complaint will be automatically categorized."
                elif any(word in message.lower() for word in ['priority', 'urgent', 'emergency']):
                    response = "Complaint priorities:\n🔴 HIGH: Emergencies, accidents, life-threatening\n🟡 MEDIUM: Important issues needing attention\n🟢 LOW: General complaints\n\nPriority is automatically detected based on your complaint content."
                else:
                    response = f"I understand you're asking about: '{message}'\n\nBased on my analysis:\n• Category: {category}\n• Priority: {priority}\n• Sentiment: {sentiment_label}\n\nHow else can I assist you with complaint management?"
            
            # Save to chat history
            if user.is_authenticated:
                Chat.objects.create(
                    user=user,
                    message=message,
                    response=response,
                    category=category if 'category' in locals() else "General",
                    sentiment_score=sentiment_score if 'sentiment_score' in locals() else 0.5,
                    classification=sentiment_label if 'sentiment_label' in locals() else "Neutral",
                    status="ai_assistant",
                    created_at=timezone.now()
                )
            
            return JsonResponse({
                'response': response,
                'category': category if 'category' in locals() else "General",
                'priority': priority if 'priority' in locals() else "Medium",
                'sentiment': sentiment_label if 'sentiment_label' in locals() else "Neutral"
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)