import re
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
# Secret key for session usage
app.secret_key = 'cyberguard_ai_secret_key_for_youtube_tutorial'

# Global in-memory statistics tracker (resets on server restart)
# Perfect for a beginner tutorial without database overhead
stats = {
    'scans_today': 0,
    'threats_found': 0,
    'safe_reports': 0,
    'total_risk': 0.0
}

def is_ip_address(domain):
    """Checks if a domain string is a raw IPv4 address."""
    clean_domain = domain.split(':')[0]
    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    return bool(re.match(ip_pattern, clean_domain))

def risk_score(percent):
    """Categorizes threats into Safe, Warning, or Danger states."""
    if percent == 0:
        return "Safe", "safe"
    elif percent <= 50:
        return "Warning", "warning"
    else:
        return "Danger", "danger"

def update_statistics(risk_percent):
    """Updates global counters for the Dashboard tab."""
    global stats
    stats['scans_today'] += 1
    stats['total_risk'] += risk_percent
    if risk_percent >= 40:  # Medium and High risks are classified as threats
        stats['threats_found'] += 1
    else:
        stats['safe_reports'] += 1

# =========================================================================
# THREAT DETECTION LOGIC FUNCTIONS
# =========================================================================

def check_url(url):
    """
    Analyzes a URL for heuristic indicator variables:
    1. Lack of HTTPS protocol
    2. Contains suspicious phish-bait keywords
    3. Uses raw IP address instead of domain names
    4. URL is excessively long (>75 chars)
    """
    parsed = urlparse(url)
    domain = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
    
    indicators = []
    
    # Rule 1: SSL Check
    if not url.lower().startswith('https://'):
        indicators.append("Unencrypted connection: URL does not use secure HTTPS protocol.")
    
    # Rule 2: Suspicious Words check
    phish_keywords = ['login', 'verify', 'bank', 'update', 'paypal', 'secure', 'free', 'gift', 'signin', 'account', 'pay', 'bonus', 'claim', 'credential']
    found_keywords = [kw for kw in phish_keywords if kw in url.lower()]
    if found_keywords:
        indicators.append(f"Suspicious terminology: Contains sensitive keywords ({', '.join(found_keywords)}).")
    
    # Rule 3: Raw IP Domain
    if is_ip_address(domain):
        indicators.append("Obfuscated domain: URL directs to a raw numerical IP address instead of a verified hostname.")
    
    # Rule 4: Length check
    if len(url) > 75:
        indicators.append("Excessive length: URL character length is unusually long (>75 characters) to hide its destination.")
    
    # Each matched indicator increases risk by 25%
    risk_percent = min(len(indicators) * 25, 100)
    status, status_class = risk_score(risk_percent)
    
    return {
        'url': url,
        'risk_percent': risk_percent,
        'status': status,
        'status_class': status_class,
        'indicators': indicators
    }

def check_email(text):
    """
    Scans email body text for urgency flags and phishing trigger words.
    Categorizes threat status by unique pattern matches.
    """
    text_lower = text.lower()
    spam_words = [
        'urgent', 'verify', 'password', 'click here', 'free', 'gift', 
        'lottery', 'win', 'bank', 'login', 'account', 'paypal', 
        'immediate', 'action required', 'suspend', 'limited time'
    ]
    
    found_keywords = [kw for kw in spam_words if kw in text_lower]
    match_count = len(found_keywords)
    
    # Heuristic threat level mapping
    if match_count == 0:
        risk_percent = 0
        status = "Safe"
        status_class = "safe"
    elif match_count <= 2:
        risk_percent = 40
        status = "Medium Warning"
        status_class = "warning"
    else:
        risk_percent = 85
        status = "High Threat"
        status_class = "danger"
        
    return {
        'found_keywords': found_keywords,
        'risk_percent': risk_percent,
        'status': status,
        'status_class': status_class,
        'match_count': match_count
    }

def password_strength(password):
    """
    Checks standard character complexity rules:
    - Length (minimum 8 chars)
    - Contains Uppercase letters
    - Contains Lowercase letters
    - Contains Numeric digits
    - Contains Special character characters
    """
    checklist = {
        'length': len(password) >= 8,
        'uppercase': any(c.isupper() for c in password),
        'lowercase': any(c.islower() for c in password),
        'number': any(c.isdigit() for c in password),
        'special': any(c in '@#$%^&*!_-+=~' for c in password)
    }
    
    score = sum(1 for match in checklist.values() if match)
    
    # Calculate status and fake 'risk' profile for dynamic dashboard calculations
    if score <= 2:
        status = "Weak"
        status_class = "danger"
        risk_percent = 90
    elif score <= 4:
        status = "Medium"
        status_class = "warning"
        risk_percent = 45
    else:
        status = "Strong"
        status_class = "safe"
        risk_percent = 0
        
    return {
        'score': score,
        'status': status,
        'status_class': status_class,
        'checklist': checklist,
        'risk_percent': risk_percent
    }

# =========================================================================
# FLASK ROUTE CONTEXTS
# =========================================================================

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/url_scanner', methods=['GET', 'POST'])
def url_scanner():
    result = None
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            result = check_url(url)
            update_statistics(result['risk_percent'])
    return render_template('url_scanner.html', result=result)

@app.route('/email_scanner', methods=['GET', 'POST'])
def email_scanner():
    result = None
    if request.method == 'POST':
        email_text = request.form.get('email_text', '').strip()
        if email_text:
            result = check_email(email_text)
            update_statistics(result['risk_percent'])
    return render_template('email_scanner.html', result=result)

@app.route('/password_checker', methods=['GET', 'POST'])
def password_checker():
    result = None
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        if password:
            result = password_strength(password)
            update_statistics(result['risk_percent'])
    return render_template('password_checker.html', result=result)

@app.route('/privacy_tips')
def privacy_tips():
    return render_template('privacy_tips.html')

@app.route('/dashboard')
def dashboard_view():
    # Calculate average risk safety metrics dynamically
    total_scans = stats['scans_today']
    avg_risk = 0.0
    if total_scans > 0:
        avg_risk = round(stats['total_risk'] / total_scans, 1)
        
    return render_template('dashboard.html', stats=stats, avg_risk=avg_risk)

# Endpoint for AJAX/JSON calls to make real-time updates simple in Javascript
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json() or {}
    scan_type = data.get('type')
    payload = data.get('payload', '')
    
    if not scan_type or not payload:
        return jsonify({'error': 'Missing type or payload parameters'}), 400
        
    if scan_type == 'url':
        res = check_url(payload)
    elif scan_type == 'email':
        res = check_email(payload)
    elif scan_type == 'password':
        res = password_strength(payload)
    else:
        return jsonify({'error': 'Invalid scan type'}), 400
        
    update_statistics(res['risk_percent'])
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
