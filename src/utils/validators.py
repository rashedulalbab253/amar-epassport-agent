"""
Input Validation and Parsing Utilities
Handles natural language input parsing and structured validation.
"""

import re
import logging
from typing import Optional
from src.models.applicant import (
    ApplicantProfile,
    DeliveryType,
    PageCount,
    Profession,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Keyword Mappings for Natural Language Parsing
# ─────────────────────────────────────────────────────────────
PROFESSION_KEYWORDS = {
    "government": ["government", "govt", "sarkari", "সরকারি"],
    "private_sector": ["private", "corporate", "company", "বেসরকারি", "প্রাইভেট"],
    "business": ["business", "entrepreneur", "trader", "ব্যবসা", "ব্যবসায়ী"],
    "student": ["student", "university", "college", "school", "শিক্ষার্থী", "ছাত্র"],
    "doctor": ["doctor", "physician", "medical", "চিকিৎসক", "ডাক্তার"],
    "engineer": ["engineer", "engineering", "প্রকৌশলী", "ইঞ্জিনিয়ার"],
    "lawyer": ["lawyer", "advocate", "attorney", "barrister", "আইনজীবী"],
    "teacher": ["teacher", "professor", "lecturer", "শিক্ষক"],
    "housewife": ["housewife", "homemaker", "গৃহিণী"],
    "unemployed": ["unemployed", "jobless", "বেকার"],
    "retired": ["retired", "pension", "অবসরপ্রাপ্ত"],
}

DELIVERY_KEYWORDS = {
    "super_express": ["super express", "super-express", "superexpress", "emergency", "2 day", "3 day", "সুপার এক্সপ্রেস"],
    "express": ["express", "urgent", "urgently", "fast", "quick", "জরুরি", "দ্রুত"],
    "regular": ["regular", "normal", "standard", "সাধারণ"],
}


def extract_age(text: str) -> Optional[int]:
    """Extract age from natural language text."""
    # Patterns like "24-year-old", "24 year old", "age 24", "I am 24"
    patterns = [
        r"(\d{1,3})\s*[-]?\s*year\s*[-]?\s*old",
        r"age\s*[-:]?\s*(\d{1,3})",
        r"i\s+am\s+(\d{1,3})",
        r"(\d{1,3})\s*বছর",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            age = int(match.group(1))
            if 0 <= age <= 120:
                return age
    return None


def extract_profession(text: str) -> Optional[str]:
    """Extract profession from natural language text."""
    text_lower = text.lower()
    for profession, keywords in PROFESSION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return profession
    return None


def extract_delivery_type(text: str) -> Optional[str]:
    """Extract delivery type from natural language text."""
    text_lower = text.lower()
    # Check super_express first since it contains "express"
    for delivery, keywords in DELIVERY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return delivery
    return None


def extract_page_count(text: str) -> Optional[int]:
    """Extract page count from natural language text."""
    text_lower = text.lower()
    if "64" in text_lower or "64-page" in text_lower:
        return 64
    if "48" in text_lower or "48-page" in text_lower:
        return 48
    return None


def extract_has_nid(text: str) -> Optional[bool]:
    """Check if the user mentions having an NID."""
    text_lower = text.lower()
    nid_keywords = ["nid", "national id", "smart card", "জাতীয় পরিচয়পত্র"]
    for kw in nid_keywords:
        if kw in text_lower:
            # Check for negation
            negation_pattern = rf"(no|don\'t have|without|নেই)\s+.*{kw}|{kw}.*\s+(no|নেই)"
            if re.search(negation_pattern, text_lower):
                return False
            return True
    return None


def extract_district(text: str) -> Optional[str]:
    """Extract district from natural language text."""
    # List of major Bangladesh districts
    districts = [
        "Dhaka", "Chittagong", "Chattogram", "Rajshahi", "Khulna",
        "Barisal", "Barishal", "Sylhet", "Rangpur", "Mymensingh",
        "Comilla", "Cumilla", "Gazipur", "Narayanganj", "Tongi",
    ]
    text_lower = text.lower()
    for district in districts:
        if district.lower() in text_lower:
            return district
    return None


def parse_user_input(text: str) -> ApplicantProfile:
    """
    Parse natural language input into a structured ApplicantProfile.

    Args:
        text: Free-form text describing the applicant's situation.

    Returns:
        ApplicantProfile with extracted data.

    Raises:
        ValueError: If required fields cannot be extracted.
    """
    logger.info(f"Parsing user input: {text[:100]}...")

    age = extract_age(text)
    if age is None:
        raise ValueError(
            "Could not determine age from input. "
            "Please specify your age (e.g., 'I am 24 years old')."
        )

    profession_str = extract_profession(text)
    if profession_str is None:
        profession_str = "other"
        logger.warning("Could not determine profession, defaulting to 'other'")

    # Auto-set profession for minors
    if age < 18 and profession_str not in ("student", "minor"):
        profession_str = "minor"

    delivery_str = extract_delivery_type(text)
    if delivery_str is None:
        delivery_str = "regular"
        logger.warning("Could not determine delivery type, defaulting to 'regular'")

    page_count = extract_page_count(text)
    if page_count is None:
        page_count = 48
        logger.warning("Could not determine page count, defaulting to 48")

    has_nid = extract_has_nid(text)
    if has_nid is None:
        has_nid = age >= 18  # Default: assume NID if adult

    district = extract_district(text)
    if district is None:
        district = "Dhaka"  # Default

    # Check for name change mentions
    name_change_keywords = ["name change", "changed name", "marriage", "নাম পরিবর্তন"]
    has_name_change = any(kw in text.lower() for kw in name_change_keywords)

    # Check for renewal mentions
    renewal_keywords = ["renewal", "renew", "নবায়ন"]
    is_renewal = any(kw in text.lower() for kw in renewal_keywords)

    # Determine requested validity
    requested_validity = None
    if "10 year" in text.lower() or "10-year" in text.lower() or "১০ বছর" in text.lower():
        requested_validity = 10
    elif "5 year" in text.lower() or "5-year" in text.lower() or "৫ বছর" in text.lower():
        requested_validity = 5

    profile = ApplicantProfile(
        age=age,
        profession=Profession(profession_str),
        delivery_type=DeliveryType(delivery_str),
        page_count=PageCount(page_count),
        has_nid=has_nid,
        has_birth_certificate=True,
        district=district,
        is_renewal=is_renewal,
        has_name_change=has_name_change,
        requested_validity_years=requested_validity,
        additional_notes=text,
    )

    logger.info(f"Parsed profile: age={age}, profession={profession_str}, delivery={delivery_str}")
    return profile
