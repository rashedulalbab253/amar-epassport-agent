"""
Bangladesh E-Passport Policy Rules Database
Local fallback data source for eligibility and policy determination.
Source: Department of Immigration & Passports, Bangladesh.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class PolicyRule:
    """Represents a passport policy rule."""
    allowed_validity_years: List[int]
    required_id_type: str
    required_id_type_bn: str
    additional_requirements: List[str] = field(default_factory=list)
    additional_requirements_bn: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    restrictions_bn: List[str] = field(default_factory=list)
    notes: str = ""
    notes_bn: str = ""


class PolicyDatabase:
    """
    Local database of Bangladesh E-Passport policies and eligibility rules.
    Acts as a fallback when external data sources are unavailable.
    """

    # ─────────────────────────────────────────────────────────────
    # Age-Based Policy Rules
    # ─────────────────────────────────────────────────────────────
    AGE_POLICIES: Dict[str, PolicyRule] = {
        "minor": PolicyRule(
            allowed_validity_years=[5],
            required_id_type="Birth Registration Certificate (BRC)",
            required_id_type_bn="জন্ম নিবন্ধন সনদ",
            additional_requirements=[
                "Parent's/Legal Guardian's NID (both parents if available)",
                "Parent's/Legal Guardian's Passport copy (if available)",
                "School/Institution ID card (if applicable)",
                "Court order (if parents are divorced/separated)",
            ],
            additional_requirements_bn=[
                "পিতা/মাতা/আইনি অভিভাবকের জাতীয় পরিচয়পত্র (উভয় পিতামাতা থাকলে)",
                "পিতা/মাতা/আইনি অভিভাবকের পাসপোর্ট কপি (থাকলে)",
                "স্কুল/প্রতিষ্ঠানের পরিচয়পত্র (প্রযোজ্য হলে)",
                "আদালতের আদেশ (পিতামাতা বিবাহবিচ্ছেদ/পৃথক হলে)",
            ],
            restrictions=[
                "Maximum validity: 5 years ONLY",
                "10-year passport NOT permitted for applicants under 18",
                "Must have a parent or legal guardian as co-applicant",
            ],
            restrictions_bn=[
                "সর্বোচ্চ মেয়াদ: শুধুমাত্র ৫ বছর",
                "১৮ বছরের কম বয়সী আবেদনকারীদের জন্য ১০ বছরের পাসপোর্ট অনুমোদিত নয়",
                "পিতা/মাতা বা আইনি অভিভাবককে সহ-আবেদনকারী হতে হবে",
            ],
            notes="Minors (under 18) are restricted to 5-year passports. NID is not issued to persons under 18; Birth Registration Certificate is the primary identification document.",
            notes_bn="নাবালকদের (১৮ বছরের কম) শুধুমাত্র ৫ বছরের পাসপোর্ট দেওয়া হয়। ১৮ বছরের কম বয়সীদের জাতীয় পরিচয়পত্র প্রদান করা হয় না; জন্ম নিবন্ধন সনদই প্রাথমিক পরিচয় দলিল।",
        ),
        "adult": PolicyRule(
            allowed_validity_years=[5, 10],
            required_id_type="National ID Card (NID / Smart Card)",
            required_id_type_bn="জাতীয় পরিচয়পত্র (NID / স্মার্ট কার্ড)",
            additional_requirements=[
                "Birth Registration Certificate (as supporting document)",
            ],
            additional_requirements_bn=[
                "জন্ম নিবন্ধন সনদ (সহায়ক দলিল হিসেবে)",
            ],
            restrictions=[],
            restrictions_bn=[],
            notes="Adults (18-65) may apply for either 5-year or 10-year passports. NID is the mandatory primary identification document.",
            notes_bn="প্রাপ্তবয়স্করা (১৮-৬৫) ৫ বছর বা ১০ বছরের পাসপোর্টের জন্য আবেদন করতে পারেন। জাতীয় পরিচয়পত্র বাধ্যতামূলক প্রাথমিক পরিচয় দলিল।",
        ),
        "senior": PolicyRule(
            allowed_validity_years=[5],
            required_id_type="National ID Card (NID / Smart Card)",
            required_id_type_bn="জাতীয় পরিচয়পত্র (NID / স্মার্ট কার্ড)",
            additional_requirements=[
                "Birth Registration Certificate (as supporting document)",
                "Medical fitness certificate (may be required)",
            ],
            additional_requirements_bn=[
                "জন্ম নিবন্ধন সনদ (সহায়ক দলিল হিসেবে)",
                "চিকিৎসা সক্ষমতা সনদ (প্রয়োজন হতে পারে)",
            ],
            restrictions=[
                "Maximum validity: 5 years ONLY",
                "10-year passport NOT permitted for applicants over 65",
            ],
            restrictions_bn=[
                "সর্বোচ্চ মেয়াদ: শুধুমাত্র ৫ বছর",
                "৬৫ বছরের ঊর্ধ্বে আবেদনকারীদের জন্য ১০ বছরের পাসপোর্ট অনুমোদিত নয়",
            ],
            notes="Senior citizens (over 65) are restricted to 5-year passports only.",
            notes_bn="প্রবীণ নাগরিকদের (৬৫ বছরের ঊর্ধ্বে) শুধুমাত্র ৫ বছরের পাসপোর্ট দেওয়া হয়।",
        ),
    }

    @classmethod
    def get_age_category(cls, age: int) -> str:
        """Determine age category from age."""
        if age < 18:
            return "minor"
        elif age > 65:
            return "senior"
        return "adult"

    @classmethod
    def get_policy(cls, age: int) -> Optional[Dict]:
        """
        Get the policy rules for an applicant based on their age.

        Args:
            age: Applicant's age in years.

        Returns:
            Dictionary with policy details, or None if invalid.
        """
        category = cls.get_age_category(age)
        rule = cls.AGE_POLICIES.get(category)

        if not rule:
            return None

        return {
            "age": age,
            "age_category": category,
            "allowed_validity_years": rule.allowed_validity_years,
            "required_id_type": rule.required_id_type,
            "required_id_type_bn": rule.required_id_type_bn,
            "additional_requirements": rule.additional_requirements,
            "additional_requirements_bn": rule.additional_requirements_bn,
            "restrictions": rule.restrictions,
            "restrictions_bn": rule.restrictions_bn,
            "notes": rule.notes,
            "notes_bn": rule.notes_bn,
            "source": "Local Database — Bangladesh Passport Policy Rules",
        }

    @classmethod
    def validate_validity_request(cls, age: int, requested_years: int) -> Dict:
        """
        Validate if a requested validity period is allowed for the given age.

        Returns:
            Dictionary with validation result and any flags/warnings.
        """
        category = cls.get_age_category(age)
        rule = cls.AGE_POLICIES.get(category)

        if not rule:
            return {
                "valid": False,
                "flag": "ERROR",
                "message": f"Unable to determine policy for age {age}.",
                "message_bn": f"{age} বছর বয়সের জন্য নীতি নির্ধারণ করা সম্ভব হয়নি।",
            }

        if requested_years in rule.allowed_validity_years:
            return {
                "valid": True,
                "flag": None,
                "message": f"{requested_years}-year passport is permitted for age {age} ({category}).",
                "message_bn": f"{requested_years} বছরের পাসপোর্ট {age} বছর বয়সে ({category}) অনুমোদিত।",
            }

        # Flag the inconsistency
        allowed = ", ".join(str(y) for y in rule.allowed_validity_years)
        return {
            "valid": False,
            "flag": "INCONSISTENCY_FLAGGED",
            "message": (
                f"⚠️ POLICY VIOLATION: A {requested_years}-year passport is NOT permitted "
                f"for a {age}-year-old ({category}). "
                f"Allowed validity: {allowed} year(s) only. "
                f"The application will be automatically adjusted to {rule.allowed_validity_years[0]}-year validity."
            ),
            "message_bn": (
                f"⚠️ নীতি লঙ্ঘন: {age} বছর বয়সী ({category}) আবেদনকারীর জন্য "
                f"{requested_years} বছরের পাসপোর্ট অনুমোদিত নয়। "
                f"অনুমোদিত মেয়াদ: শুধুমাত্র {allowed} বছর। "
                f"আবেদনটি স্বয়ংক্রিয়ভাবে {rule.allowed_validity_years[0]} বছরের মেয়াদে সমন্বয় করা হবে।"
            ),
            "corrected_validity": rule.allowed_validity_years[0],
        }

    @classmethod
    def get_max_validity(cls, age: int) -> int:
        """Get the maximum allowed validity period for a given age."""
        category = cls.get_age_category(age)
        rule = cls.AGE_POLICIES.get(category)
        if rule:
            return max(rule.allowed_validity_years)
        return 5  # Default to safest option
