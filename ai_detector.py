"""
🤖 AI-POWERED PRESCRIPTION FORGERY DETECTION SYSTEM
====================================================
Advanced OCR and Machine Learning based prescription verification
Author: Enhanced Medical System
Version: 2.0
"""

import pytesseract
import cv2
import numpy as np
import re
from datetime import datetime

# Configure Tesseract path (Windows users - update this path)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ========== IMAGE PREPROCESSING ==========

def enhance_image(image):
    """
    Advanced image preprocessing for better OCR accuracy
    """
    try:
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        # Morphological operations to remove noise
        kernel = np.ones((1, 1), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return morph
    except Exception as e:
        print(f"⚠️ Image enhancement error: {e}")
        return image

def extract_text(image_path):
    """
    Extract text from prescription image with advanced preprocessing
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Cannot read image: {image_path}")
            return ""
        
        # Enhance image
        enhanced = enhance_image(img)
        
        # OCR with multiple configurations
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(enhanced, config=custom_config)
        
        print(f"✅ Extracted {len(text)} characters from image")
        return text
    except Exception as e:
        print(f"❌ Text extraction error: {e}")
        return ""

# ========== ADVANCED DETECTION ALGORITHMS ==========

def check_required_fields(text):
    """
    Check for essential prescription fields
    Returns: (score, found_fields)
    """
    text_lower = text.lower()
    score = 0
    found_fields = []
    
    fields = {
        'doctor': [r'dr\.?\s+\w+', r'doctor\s+\w+', r'physician', r'mbbs', r'md'],
        'patient': [r'patient\s*:?\s*\w+', r'name\s*:?\s*\w+', r'mr\.?|mrs\.?|ms\.?'],
        'date': [r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', r'\d{1,2}\s+\w+\s+\d{4}'],
        'medicine': [r'medicine|medication|drug|rx|prescription', r'tablet|capsule|syrup|injection'],
        'dosage': [r'\d+\s*mg|ml|g', r'twice|thrice|daily|weekly', r'morning|evening|night'],
        'signature': [r'signature|signed|dr\.?\s+signature', r'seal|stamp'],
        'clinic': [r'clinic|hospital|medical\s+center', r'healthcare'],
    }
    
    for field, patterns in fields.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                score += 15
                found_fields.append(field)
                break  # Count each field only once
    
    return score, found_fields

def check_format_authenticity(text):
    """
    Check if prescription follows medical format standards
    """
    score = 0
    
    # Medical abbreviations
    medical_terms = [
        'rx', 'sig', 'disp', 'bid', 'tid', 'qid', 'od', 'bd', 
        'prn', 'stat', 'hs', 'ac', 'pc', 'po', 'im', 'iv'
    ]
    
    text_lower = text.lower()
    for term in medical_terms:
        if f' {term} ' in f' {text_lower} ':
            score += 5
    
    # Structured format indicators
    structure_patterns = [
        r'Rx\s*:',
        r'Diagnosis\s*:',
        r'Symptoms\s*:',
        r'Instructions\s*:',
        r'\d+\.\s+\w+',  # Numbered list
    ]
    
    for pattern in structure_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score += 10
    
    return min(score, 50)

def check_suspicious_patterns(text):
    """
    Detect suspicious or fraudulent patterns
    Returns: (penalty_score, suspicious_items)
    """
    penalty = 0
    suspicious_items = []
    
    text_lower = text.lower()
    
    # Red flags
    red_flags = {
        'fake indicators': ['fake', 'forged', 'duplicate', 'copy', 'photocopy', 'scanned'],
        'invalid markers': ['not valid', 'void', 'cancelled', 'expired', 'invalid'],
        'suspicious words': ['test', 'sample', 'demo', 'practice'],
    }
    
    for category, words in red_flags.items():
        for word in words:
            if word in text_lower:
                penalty += 20
                suspicious_items.append(f"{category}: '{word}'")
    
    return penalty, suspicious_items

def analyze_text_quality(text):
    """
    Analyze overall quality of extracted text
    """
    if not text or len(text.strip()) < 10:
        return 0, "Too little text extracted"
    
    # Character diversity (medical docs have good mix)
    unique_chars = len(set(text))
    char_score = min(unique_chars / 2, 30)
    
    # Word count
    words = text.split()
    word_score = min(len(words) * 2, 30)
    
    # Uppercase/lowercase ratio (normal docs have both)
    upper_count = sum(1 for c in text if c.isupper())
    lower_count = sum(1 for c in text if c.islower())
    
    if upper_count > 0 and lower_count > 0:
        ratio_score = 20
    else:
        ratio_score = 0
    
    total_score = char_score + word_score + ratio_score
    
    quality = "High" if total_score > 60 else "Medium" if total_score > 30 else "Low"
    
    return total_score, quality

def check_date_validity(text):
    """
    Check if prescription has valid date
    """
    date_patterns = [
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
        r'\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return 15, match.group()
    
    return 0, None

# ========== MAIN DETECTION FUNCTION ==========

def detect_forgery(image_path):
    """
    🤖 Advanced AI-powered prescription forgery detection
    
    Multi-layer analysis:
    - Text extraction with OCR
    - Required fields validation
    - Format authenticity check
    - Suspicious pattern detection
    - Text quality analysis
    - Date validity check
    
    Returns: (status, confidence_percentage)
    Status: "Original" | "Suspicious" | "Fake"
    """
    
    print(f"\n{'='*60}")
    print(f"🔍 Starting AI Forgery Detection Analysis")
    print(f"{'='*60}")
    
    # Extract text
    text = extract_text(image_path)
    
    if not text or len(text.strip()) < 20:
        print("❌ Insufficient text extracted - Likely FAKE")
        return "Fake", 15.0
    
    print(f"📝 Extracted Text Length: {len(text)} characters")
    print(f"📝 Word Count: {len(text.split())} words")
    
    # Initialize scoring
    total_score = 0
    max_score = 200
    
    # Analysis 1: Required Fields (max 105 points)
    field_score, found_fields = check_required_fields(text)
    total_score += field_score
    print(f"✅ Required Fields Score: {field_score}/105")
    print(f"   Found: {', '.join(found_fields) if found_fields else 'None'}")
    
    # Analysis 2: Format Authenticity (max 50 points)
    format_score = check_format_authenticity(text)
    total_score += format_score
    print(f"✅ Format Score: {format_score}/50")
    
    # Analysis 3: Text Quality (max 80 points)
    quality_score, quality_level = analyze_text_quality(text)
    total_score += quality_score
    print(f"✅ Text Quality: {quality_level} ({quality_score}/80 points)")
    
    # Analysis 4: Date Validity (max 15 points)
    date_score, found_date = check_date_validity(text)
    total_score += date_score
    if found_date:
        print(f"✅ Date Found: {found_date} ({date_score} points)")
    else:
        print(f"⚠️ No valid date found")
    
    # Analysis 5: Suspicious Patterns (penalty)
    penalty, suspicious_items = check_suspicious_patterns(text)
    total_score -= penalty
    if suspicious_items:
        print(f"⚠️ Suspicious Patterns Detected: -{penalty} points")
        for item in suspicious_items:
            print(f"   - {item}")
    
    # Calculate confidence percentage
    confidence = (total_score / max_score) * 100
    confidence = max(0, min(100, confidence))
    
    # Determine status
    if confidence >= 70:
        status = "Original"
        emoji = "✅"
    elif confidence >= 40:
        status = "Suspicious"
        emoji = "⚠️"
    else:
        status = "Fake"
        emoji = "❌"
    
    print(f"\n{'='*60}")
    print(f"{emoji} FINAL VERDICT: {status}")
    print(f"🎯 Confidence Score: {confidence:.1f}%")
    print(f"{'='*60}\n")
    
    return status, confidence

# ========== ADDITIONAL UTILITY FUNCTIONS ==========

def get_detection_details(image_path):
    """
    Get detailed analysis report for an image
    Returns dictionary with all detection metrics
    """
    text = extract_text(image_path)
    
    if not text:
        return {
            'status': 'Error',
            'confidence': 0,
            'error': 'Could not extract text from image'
        }
    
    field_score, found_fields = check_required_fields(text)
    format_score = check_format_authenticity(text)
    quality_score, quality_level = analyze_text_quality(text)
    date_score, found_date = check_date_validity(text)
    penalty, suspicious_items = check_suspicious_patterns(text)
    
    status, confidence = detect_forgery(image_path)
    
    return {
        'status': status,
        'confidence': confidence,
        'text_length': len(text),
        'word_count': len(text.split()),
        'found_fields': found_fields,
        'field_score': field_score,
        'format_score': format_score,
        'quality_score': quality_score,
        'quality_level': quality_level,
        'date_found': found_date,
        'suspicious_items': suspicious_items,
        'penalty': penalty,
        'extracted_text_preview': text[:200] + '...' if len(text) > 200 else text
    }

def batch_detect(image_paths):
    """
    Analyze multiple prescriptions at once
    """
    results = []
    for i, path in enumerate(image_paths, 1):
        print(f"\n📋 Analyzing prescription {i}/{len(image_paths)}: {path}")
        status, confidence = detect_forgery(path)
        results.append({
            'path': path,
            'status': status,
            'confidence': confidence
        })
    return results

# ========== TESTING ==========

if __name__ == "__main__":
    print("🏥 AI Prescription Forgery Detection System")
    print("=" * 60)
    print("Ready to analyze prescriptions!")
    print("\nUsage:")
    print("  from ai_detector import detect_forgery")
    print("  status, confidence = detect_forgery('prescription.jpg')")
    print("=" * 60)