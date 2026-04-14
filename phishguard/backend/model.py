# This file contains the REAL phishing detection logic
# No fake data - it analyzes every URL mathematically

import re
from urllib.parse import urlparse
import math

def extract_features(url):
    """
    Extract numerical features from ANY URL.
    These features are what the ML model uses to decide if it's phishing.
    """
    
    features = {}
    
    # Feature 1: URL Length (phishing URLs are often very long)
    features['length'] = len(url)
    # Normalize: divide by 100 to keep number reasonable (0-5 range typically)
    
    # Feature 2: Has HTTPS? (phishing often lacks HTTPS)
    features['has_https'] = 1 if url.startswith('https://') else 0
    
    # Feature 3: Number of dots (more dots = more subdomains = suspicious)
    features['dot_count'] = url.count('.')
    
    # Feature 4: Number of hyphens (phishing uses hyphens like paypal-secure.com)
    features['hyphen_count'] = url.count('-')
    
    # Feature 5: Has @ symbol? (URLs with @ are very suspicious - used for redirect tricks)
    features['has_at_symbol'] = 1 if '@' in url else 0
    
    # Feature 6: Contains IP address instead of domain name? (Highly suspicious)
    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    features['has_ip_address'] = 1 if re.search(ip_pattern, url) else 0
    
    # Feature 7: Count suspicious keywords (words phishers love to use)
    suspicious_words = ['login', 'verify', 'secure', 'account', 'update', 
                        'bank', 'paypal', 'signin', 'confirm', 'validate',
                        'unlock', 'alert', 'warning', 'urgent', 'security']
    
    count = 0
    url_lower = url.lower()
    for word in suspicious_words:
        if word in url_lower:
            count += 1
    features['suspicious_word_count'] = count
    
    # Feature 8: Number of subdomains (more subdomains = more suspicious)
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc
        # Count parts before main domain
        parts = netloc.split('.')
        if len(parts) >= 3:
            features['subdomain_count'] = len(parts) - 2
        else:
            features['subdomain_count'] = 0
    except:
        features['subdomain_count'] = 0
    
    # Feature 9: Has redirect? (look for double slash after domain)
    try:
        after_domain = url.split('//')[1] if '//' in url else url
        if '//' in after_domain:
            features['has_redirect'] = 1
        else:
            features['has_redirect'] = 0
    except:
        features['has_redirect'] = 0
    
    # Feature 10: Check for typosquatting (common brands misspelled)
    brand_patterns = {
        'paypal': ['paypa1', 'paypaI', 'paypall', 'pay-pal'],
        'google': ['go0gle', 'g00gle', 'goog1e', 'go-ogle'],
        'amazon': ['amaz0n', 'amazom', 'amazzon', 'amaz-on'],
        'facebook': ['faceb00k', 'facebo0k', 'face-book'],
        'microsoft': ['micr0soft', 'micros0ft', 'micro-soft'],
        'apple': ['app1e', 'appIe', 'app-le'],
        'netflix': ['netfl1x', 'netfliix', 'net-flix']
    }
    
    features['typosquat_score'] = 0
    url_lower = url.lower()
    for brand, typos in brand_patterns.items():
        if brand in url_lower:
            # Legitimate brand mention - good sign
            features['typosquat_score'] -= 1
        for typo in typos:
            if typo in url_lower:
                features['typosquat_score'] += 2  # High penalty
    
    # Feature 11: Check for URL shortening services (often used to hide phishing)
    shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly', 'adf.ly']
    features['is_shortened'] = 1 if any(s in url_lower for s in shorteners) else 0
    
    return features


def predict_url(url):
    """
    This is the MAIN prediction logic.
    Takes a URL, extracts features, applies rules, returns result.
    No pre-stored data - works on ANY URL you give it.
    """
    
    features = extract_features(url)
    
    # Start with a base score of 0 (neutral)
    # Positive = more likely phishing, Negative = more likely safe
    phishing_score = 0
    reasons = []
    
    # === RULE 1: HTTPS ===
    if features['has_https'] == 1:
        phishing_score -= 30  # Good: has HTTPS, less likely phishing
        reasons.append("✅ Has HTTPS encryption")
    else:
        phishing_score += 40  # Bad: no HTTPS
        reasons.append("🔴 No HTTPS encryption")
    
    # === RULE 2: URL Length ===
    if features['length'] > 75:
        phishing_score += 25
        reasons.append("⚠️ Unusually long URL")
    elif features['length'] < 40:
        phishing_score -= 10
        reasons.append("✅ Short, clean URL")
    
    # === RULE 3: Suspicious keywords ===
    if features['suspicious_word_count'] >= 2:
        phishing_score += 30
        reasons.append(f"🔴 Contains {features['suspicious_word_count']} suspicious keywords")
    elif features['suspicious_word_count'] == 1:
        phishing_score += 15
        reasons.append(f"⚠️ Contains suspicious keyword")
    else:
        phishing_score -= 5
    
    # === RULE 4: @ symbol ===
    if features['has_at_symbol'] == 1:
        phishing_score += 50  # Very suspicious
        reasons.append("🚨 Contains @ symbol (redirect trick)")
    
    # === RULE 5: IP address ===
    if features['has_ip_address'] == 1:
        phishing_score += 60  # Extremely suspicious
        reasons.append("🚨 Uses IP address instead of domain name")
    
    # === RULE 6: Multiple subdomains ===
    if features['subdomain_count'] >= 3:
        phishing_score += 25
        reasons.append(f"⚠️ {features['subdomain_count']} subdomains (excessive)")
    elif features['subdomain_count'] == 2:
        phishing_score += 10
        reasons.append(f"⚠️ Multiple subdomains")
    
    # === RULE 7: Many dots ===
    if features['dot_count'] >= 5:
        phishing_score += 20
        reasons.append("⚠️ Unusual number of dots")
    
    # === RULE 8: Many hyphens ===
    if features['hyphen_count'] >= 3:
        phishing_score += 15
        reasons.append("⚠️ Multiple hyphens (typosquatting pattern)")
    
    # === RULE 9: Typosquatting ===
    if features['typosquat_score'] >= 2:
        phishing_score += 35
        reasons.append("🚨 Possible typosquatting (fake brand name)")
    elif features['typosquat_score'] <= -1:
        phishing_score -= 15
        reasons.append("✅ Known legitimate brand detected")
    
    # === RULE 10: URL shortener ===
    if features['is_shortened'] == 1:
        phishing_score += 20
        reasons.append("⚠️ Shortened URL (hides real destination)")
    
    # === RULE 11: Redirect ===
    if features['has_redirect'] == 1:
        phishing_score += 15
        reasons.append("⚠️ Contains redirect")
    
    # === FINAL DECISION based on score ===
    # Score range typically -50 to +150
    
    if phishing_score <= 10:
        label = "Safe"
        confidence = max(50, 100 - (phishing_score + 50))
        if confidence > 98:
            confidence = 98
    elif phishing_score <= 45:
        label = "Suspicious"
        confidence = 50 + (phishing_score - 10) // 1
    else:
        label = "Phishing"
        confidence = min(98, 50 + (phishing_score - 45) // 1)
    
    confidence = round(confidence, 1)
    
    # Clean up reasons for display
    if label == "Safe":
        if not reasons or all("✅" in r for r in reasons):
            reasons.append("✅ URL appears legitimate")
    elif label == "Phishing":
        reasons.insert(0, "🚨 DANGEROUS: This link is likely a phishing attempt!")
    
    # Keep only top 4 reasons for display
    reasons = reasons[:4]
    
    return {
        "label": label,
        "confidence": confidence,
        "reasons": reasons,
        "features": features  # Included for debugging/demo
    }


# Test function - run this directly to see if it works
if __name__ == "__main__":
    # Test URLs
    test_urls = [
        "https://www.google.com",
        "http://paypa1-secure-login.com/verify",
        "https://amazon.com/login",
        "http://192.168.1.1/paypal/update",
        "https://bit.ly/3xK92p"
    ]
    
    print("=" * 60)
    print("TESTING PHISHING DETECTION MODEL")
    print("=" * 60)
    
    for url in test_urls:
        result = predict_url(url)
        print(f"\n📎 URL: {url}")
        print(f"   Label: {result['label']}")
        print(f"   Confidence: {result['confidence']}%")
        print(f"   Reasons: {', '.join(result['reasons'])}")