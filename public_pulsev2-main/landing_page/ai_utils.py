"""
AI Utilities for Complaint Analysis
"""
import re
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('vader_lexicon')


def categorize_complaint(text):
    """AI-based categorization using advanced keyword matching"""
    text = text.lower()
    
    categories = {
        'Municipal Issues': [
            'road', 'garbage', 'water', 'street', 'drainage', 'pothole',
            'sewage', 'sanitation', 'cleanliness', 'waste', 'street light',
            'footpath', 'public toilet', 'park', 'garden'
        ],
        'Electricity': [
            'power', 'electricity', 'current', 'transformer', 'wire',
            'blackout', 'outage', 'meter', 'bill', 'connection',
            'voltage', 'fuse', 'electric', 'light'
        ],
        'Water Supply': [
            'water', 'pipeline', 'supply', 'tanker', 'leakage',
            'drinking', 'tap', 'shortage', 'quality', 'pressure',
            'drain', 'flood', 'irrigation'
        ],
        'Healthcare': [
            'hospital', 'doctor', 'medicine', 'ambulance', 'health',
            'clinic', 'patient', 'treatment', 'emergency', 'vaccine',
            'pharmacy', 'medical', 'nurse'
        ],
        'Education': [
            'school', 'teacher', 'college', 'education', 'exam',
            'student', 'fee', 'admission', 'result', 'certificate',
            'library', 'scholarship', 'uniform', 'book'
        ],
        'Transport': [
            'bus', 'train', 'traffic', 'transport', 'road',
            'accident', 'ticket', 'schedule', 'delay', 'metro',
            'auto', 'taxi', 'parking', 'license'
        ],
        'Corruption': [
            'bribe', 'corruption', 'bribery', 'black money', 'scam',
            'fraud', 'illegal', 'embezzlement', 'kickback'
        ],
        'Public Safety': [
            'police', 'crime', 'safety', 'theft', 'robbery',
            'harassment', 'violence', 'security', 'fight'
        ],
    }
    
    # Count matches for each category
    category_scores = {}
    for category, keywords in categories.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
                # Boost score if keyword appears multiple times
                score += text.count(keyword) * 0.5
        
        if score > 0:
            category_scores[category] = score
    
    if category_scores:
        # Return category with highest score
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    return 'General'


def detect_priority(text):
    """Detect priority based on keywords and sentiment"""
    text = text.lower()
    
    # High priority keywords
    high_keywords = [
        'emergency', 'urgent', 'immediate', 'accident', 'fire',
        'hospital', 'death', 'injured', 'danger', 'critical',
        'life threatening', 'serious', 'severe', 'help immediately'
    ]
    
    # Medium priority keywords
    medium_keywords = [
        'soon', 'important', 'broken', 'not working', 'problem',
        'issue', 'difficulty', 'trouble', 'complaint', 'request'
    ]
    
    # Check for urgency indicators
    urgency_patterns = [
        r'as soon as possible',
        r'immediate attention',
        r'right now',
        r'urgently',
        r'emergency situation'
    ]
    
    # Check high priority
    for keyword in high_keywords:
        if keyword in text:
            return 'High'
    
    # Check urgency patterns
    for pattern in urgency_patterns:
        if re.search(pattern, text):
            return 'High'
    
    # Check medium priority
    for keyword in medium_keywords:
        if keyword in text:
            return 'Medium'
    
    # Check sentiment for priority
    sentiment_label, _, sentiment_score = analyze_sentiment(text)
    if sentiment_label == 'Negative' and sentiment_score < -0.5:
        return 'High'
    elif sentiment_label == 'Negative':
        return 'Medium'
    
    return 'Low'


def analyze_sentiment(text):
    """Enhanced sentiment analysis using multiple methods"""
    # Clean text
    text = text.strip()
    
    # Method 1: TextBlob
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 to 1
    subjectivity = blob.sentiment.subjectivity  # 0 to 1
    
    # Method 2: VADER (better for social media/text)
    sia = SentimentIntensityAnalyzer()
    vader_scores = sia.polarity_scores(text)
    
    # Combine scores
    combined_score = (polarity + vader_scores['compound']) / 2
    
    # Determine sentiment label
    if combined_score <= -0.3:
        label = 'Negative'
        if combined_score <= -0.7:
            insight = 'Very negative - Citizen is extremely frustrated/angry'
        elif combined_score <= -0.5:
            insight = 'Negative - Citizen is unhappy/dissatisfied'
        else:
            insight = 'Somewhat negative - Citizen has concerns'
    
    elif combined_score >= 0.3:
        label = 'Positive'
        if combined_score >= 0.7:
            insight = 'Very positive - Citizen is extremely happy/satisfied'
        elif combined_score >= 0.5:
            insight = 'Positive - Citizen is satisfied'
        else:
            insight = 'Somewhat positive - Citizen is content'
    
    else:
        label = 'Neutral'
        insight = 'Neutral - Standard complaint/request'
    
    # Additional insights based on keywords
    negative_words = ['angry', 'frustrated', 'disappointed', 'horrible', 'terrible', 'worst']
    positive_words = ['happy', 'satisfied', 'good', 'excellent', 'thank', 'appreciate']
    
    text_lower = text.lower()
    for word in negative_words:
        if word in text_lower:
            label = 'Negative'
            insight = f'Contains negative word "{word}" - Citizen expresses frustration'
            break
    
    for word in positive_words:
        if word in text_lower:
            label = 'Positive'
            insight = f'Contains positive word "{word}" - Citizen expresses satisfaction'
            break
    
    return label, insight, combined_score


def extract_keywords(text, num_keywords=10):
    """Extract important keywords from text"""
    # Tokenize and remove stopwords
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    
    # Add custom stopwords
    custom_stopwords = ['please', 'would', 'could', 'should', 'need', 'want']
    stop_words.update(custom_stopwords)
    
    # Filter tokens
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    # Get POS tags and focus on nouns and verbs
    pos_tags = pos_tag(filtered_tokens)
    important_words = []
    
    for word, tag in pos_tags:
        if tag.startswith('NN') or tag.startswith('VB'):  # Nouns and Verbs
            important_words.append(word)
    
    # Remove duplicates and get top N
    unique_words = list(set(important_words))
    
    # If we don't have enough important words, use filtered tokens
    if len(unique_words) < num_keywords:
        additional = [w for w in filtered_tokens if w not in unique_words]
        unique_words.extend(additional[:num_keywords - len(unique_words)])
    
    return unique_words[:num_keywords]


def generate_ai_summary(complaint_text, category, sentiment):
    """Generate AI summary of complaint"""
    keywords = extract_keywords(complaint_text, 5)
    
    summary = f"""
    Complaint Analysis Summary:
    - Detected Category: {category}
    - Sentiment: {sentiment}
    - Key Issues: {', '.join(keywords)}
    
    Recommended Action: {'Urgent attention required' if sentiment == 'Negative' else 'Standard processing'}
    """
    
    return summary.strip()