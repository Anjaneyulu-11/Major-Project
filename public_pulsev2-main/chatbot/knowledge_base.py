# Rule-based knowledge base for Civic Pulse assistant
# Each entry contains 'keywords' (list of strings) and 'answer' (short string)
KNOWLEDGE_BASE = [
    {
        "keywords": ["how do i lodge", "lodge", "submit", "file complaint", "file a complaint", "how to lodge"],
        "answer": "To lodge a complaint: go to 'Lodge Complaint', fill the form, add location and attachments if needed, and submit. You will receive a Complaint ID for tracking."
    },
    {
        "keywords": ["how to track", "track", "tracking", "how can i track", "check status"],
        "answer": "To track a complaint: go to 'Track Complaint', enter your Complaint ID, and view status updates. You can also see recent items in 'My Complaints'."
    },
    {
        "keywords": ["why is my complaint pending", "still pending", "pending"],
        "answer": "Pending means the complaint has been received and is awaiting assignment or action by the responsible department. Response times vary by priority and department."
    },
    {
        "keywords": ["what does resolved mean", "resolved", "what is resolved"],
        "answer": "Resolved indicates the responsible department has marked the complaint as addressed. Please review resolution details in the complaint page."
    },
    {
        "keywords": ["in progress", "inprogress", "working on"],
        "answer": "In Progress means the department is actively working on the complaint. Check the complaint details for updates and estimated timelines."
    },
    {
        "keywords": ["where can i see my complaints", "my complaints", "where are my complaints"],
        "answer": "You can view all complaints you submitted under 'My Complaints' on your dashboard. Each item links to full details."
    },
    {
        "keywords": ["dashboard usage", "dashboard", "how to use dashboard"],
        "answer": "The Dashboard summarizes your active and resolved complaints, quick actions, and recent updates. Use quick links to lodge or track complaints."
    },
    {
        "keywords": ["how do i update my profile", "update profile", "edit profile"],
        "answer": "To update your profile, go to 'Profile', edit your details, and save. Changes apply to future submissions and notifications."
    },
    {
        "keywords": ["change my username", "change username", "can i change username"],
        "answer": "Usernames are permanent. To change display information, update your name and email in the Profile page. Contact support for exceptional requests."
    },
    {
        "keywords": ["what is civic pulse", "what is public pulse", "what is this platform"],
        "answer": "Civic Pulse is an official citizen feedback portal for lodging and tracking public-service complaints and receiving status updates from responsible departments."
    },
    {
        "keywords": ["who handles my complaint", "who handles", "responsible department", "handled by"],
        "answer": "Complaints are routed to the relevant municipal or department team based on category; the department listed on the complaint page handles it."
    },
    {
        "keywords": ["how do i contact support", "contact support", "help", "support"],
        "answer": "For assistance, use the 'Contact' page or email support at support@publicpulse.example. Provide your Complaint ID when relevant."
    },
    {
        "keywords": ["attachments", "upload image", "photos", "attachments not uploading"],
        "answer": "You can attach images when lodging a complaint. If upload fails, try a smaller image or a different browser, and retry the submission."
    },
    {
        "keywords": ["email notifications", "email", "notification"],
        "answer": "We send confirmation and status emails to the address you provide. Check your spam folder and ensure your profile email is correct."
    },
    {
        "keywords": ["privacy", "data", "who can see my complaint", "public"],
        "answer": "Your personal details are used only for complaint handling and notifications. Complaint content is shared with responsible departments as needed."
    },
    {
        "keywords": ["escalate", "escalation", "not resolved", "unresolved"],
        "answer": "If a complaint is not resolved in a reasonable time, use the 'Complaint History' to note delays and contact support to request escalation."
    },
    {
        "keywords": ["timeframe", "how long", "how long will it take", "response time"],
        "answer": "Response times vary by department and priority. High-priority issues are addressed first; typical resolutions range from days to weeks."
    },
    {
        "keywords": ["status definitions", "status meaning", "meaning of status"],
        "answer": "Status definitions: Submitted (received), In Progress (work started), Resolved (action completed), Closed (case closed after verification)."
    },
    {
        "keywords": ["anonymous", "anonymous complaint", "without email"],
        "answer": "You may submit a complaint with an email for tracking. Anonymous submissions limit follow-up; include an email for full support."
    },
    {
        "keywords": ["edit complaint", "update complaint", "change complaint"],
        "answer": "Once submitted, complaints cannot be edited. Submit a follow-up complaint with updated details or contact support with the Complaint ID."
    },
    {
        "keywords": ["delete complaint", "remove complaint"],
        "answer": "Complaints are official records and cannot be deleted by users. Contact support if a record requires correction for legitimate reasons."
    },
    {
        "keywords": ["multiple complaints", "submit multiple"],
        "answer": "You may submit multiple complaints. Provide clear details and separate entries for unrelated issues to help departments act quickly."
    },
    {
        "keywords": ["mobile", "app", "mobile friendly"],
        "answer": "Civic Pulse is mobile-friendly via the website. For best results, use the latest browser and ensure a stable connection when uploading attachments."
    },
    {
        "keywords": ["feedback", "satisfaction", "rate"],
        "answer": "After resolution, you may submit feedback on the complaint page. Feedback helps improve service quality."
    },
    {
        "keywords": ["duplicate", "already submitted", "duplicate complaint"],
        "answer": "If a similar complaint exists, avoid duplication. Use the existing complaint to add comments or contact support for consolidation."
    },
    {
        "keywords": ["recover password", "forgot password", "reset password"],
        "answer": "Use the 'Forgot Password' link on the login page to reset your password. Follow the emailed instructions to complete reset securely."
    },
    {
        "keywords": ["login issues", "cannot login", "unable to login"],
        "answer": "If you cannot log in, confirm your credentials. Use password reset, or contact support with your username and email for assistance."
    },
    {
        "keywords": ["data correction", "wrong email", "update email"],
        "answer": "To correct personal details, update your Profile. For administrative corrections, contact support and include relevant Complaint IDs."
    },
    {
        "keywords": ["ai assistant purpose", "what does assistant do", "ai assistant"],
        "answer": "This assistant provides factual guidance on using Civic Pulse and common processes. It is rule-based and does not generate official policy decisions."
    },
    {
        "keywords": ["who can view", "visibility", "public view"],
        "answer": "Complaint details are visible to you and authorized department staff. Public viewing depends on local policy and redaction of personal data."
    },
    {
        "keywords": ["how to contact department", "department contact", "which department"],
        "answer": "The complaint page shows the assigned department. Use that page or contact support for department-specific contact details."
    },
    {
        "keywords": ["submit again", "resubmit", "retry submission"],
        "answer": "If submission fails, retry with a stable connection. Save screenshots and note any error messages to share with support."
    }
]
