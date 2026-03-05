"""
Applicant Profile Data Models
Pydantic models for validating and structuring applicant data.
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class DeliveryType(str, Enum):
    """Passport delivery speed options."""
    REGULAR = "regular"           # 21 working days
    EXPRESS = "express"           # 7 working days
    SUPER_EXPRESS = "super_express"  # 2-3 working days

    @property
    def label_en(self) -> str:
        labels = {
            "regular": "Regular (21 working days)",
            "express": "Express (7 working days)",
            "super_express": "Super Express (2-3 working days)",
        }
        return labels[self.value]

    @property
    def label_bn(self) -> str:
        labels = {
            "regular": "সাধারণ (২১ কার্যদিবস)",
            "express": "জরুরি (৭ কার্যদিবস)",
            "super_express": "সুপার এক্সপ্রেস (২-৩ কার্যদিবস)",
        }
        return labels[self.value]


class PageCount(int, Enum):
    """Passport page count options."""
    PAGES_48 = 48
    PAGES_64 = 64


class Profession(str, Enum):
    """Applicant profession categories."""
    GOVERNMENT = "government"
    PRIVATE_SECTOR = "private_sector"
    BUSINESS = "business"
    STUDENT = "student"
    DOCTOR = "doctor"
    ENGINEER = "engineer"
    LAWYER = "lawyer"
    TEACHER = "teacher"
    HOUSEWIFE = "housewife"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    MINOR = "minor"
    OTHER = "other"

    @property
    def label_en(self) -> str:
        labels = {
            "government": "Government Employee",
            "private_sector": "Private Sector Employee",
            "business": "Business Person",
            "student": "Student",
            "doctor": "Doctor",
            "engineer": "Engineer",
            "lawyer": "Lawyer",
            "teacher": "Teacher",
            "housewife": "Housewife",
            "unemployed": "Unemployed",
            "retired": "Retired",
            "minor": "Minor (Under 18)",
            "other": "Other",
        }
        return labels[self.value]

    @property
    def label_bn(self) -> str:
        labels = {
            "government": "সরকারি কর্মচারী",
            "private_sector": "বেসরকারি কর্মচারী",
            "business": "ব্যবসায়ী",
            "student": "শিক্ষার্থী",
            "doctor": "চিকিৎসক",
            "engineer": "প্রকৌশলী",
            "lawyer": "আইনজীবী",
            "teacher": "শিক্ষক",
            "housewife": "গৃহিণী",
            "unemployed": "বেকার",
            "retired": "অবসরপ্রাপ্ত",
            "minor": "নাবালক (১৮ বছরের কম)",
            "other": "অন্যান্য",
        }
        return labels[self.value]


class ApplicantProfile(BaseModel):
    """
    Complete applicant profile for passport application assessment.
    Validates all input fields with appropriate constraints.
    """
    age: int = Field(
        ...,
        ge=0,
        le=120,
        description="Applicant's age in years"
    )
    profession: Profession = Field(
        ...,
        description="Applicant's profession category"
    )
    delivery_type: DeliveryType = Field(
        ...,
        description="Desired passport delivery speed"
    )
    page_count: PageCount = Field(
        default=PageCount.PAGES_48,
        description="Desired passport page count (48 or 64)"
    )
    has_nid: bool = Field(
        default=False,
        description="Whether the applicant has a National ID Card"
    )
    has_birth_certificate: bool = Field(
        default=True,
        description="Whether the applicant has a Birth Registration Certificate"
    )
    district: str = Field(
        default="Dhaka",
        description="Applicant's district of residence"
    )
    is_renewal: bool = Field(
        default=False,
        description="Whether this is a passport renewal"
    )
    has_name_change: bool = Field(
        default=False,
        description="Whether the applicant has changed their name"
    )
    requested_validity_years: Optional[int] = Field(
        default=None,
        description="Requested passport validity period in years (5 or 10)"
    )
    additional_notes: Optional[str] = Field(
        default=None,
        description="Any additional notes or special circumstances"
    )

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Age cannot be negative")
        if v > 120:
            raise ValueError("Age cannot exceed 120 years")
        return v

    @field_validator("requested_validity_years")
    @classmethod
    def validate_validity(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in (5, 10):
            raise ValueError("Validity must be either 5 or 10 years")
        return v

    @property
    def is_minor(self) -> bool:
        """Check if applicant is under 18."""
        return self.age < 18

    @property
    def is_senior(self) -> bool:
        """Check if applicant is over 65."""
        return self.age > 65

    @property
    def age_category(self) -> str:
        """Get the age category for policy lookup."""
        if self.age < 18:
            return "minor"
        elif self.age > 65:
            return "senior"
        else:
            return "adult"

    @property
    def age_category_bn(self) -> str:
        """Get the age category in Bangla."""
        categories = {
            "minor": "নাবালক",
            "senior": "প্রবীণ",
            "adult": "প্রাপ্তবয়স্ক",
        }
        return categories[self.age_category]

    def to_summary(self) -> str:
        """Generate a human-readable summary of the applicant profile."""
        lines = [
            f"Age: {self.age} years ({self.age_category})",
            f"Profession: {self.profession.label_en}",
            f"Delivery Type: {self.delivery_type.label_en}",
            f"Page Count: {self.page_count.value} pages",
            f"Has NID: {'Yes' if self.has_nid else 'No'}",
            f"Has Birth Certificate: {'Yes' if self.has_birth_certificate else 'No'}",
            f"District: {self.district}",
            f"Is Renewal: {'Yes' if self.is_renewal else 'No'}",
            f"Name Change: {'Yes' if self.has_name_change else 'No'}",
        ]
        if self.requested_validity_years:
            lines.append(f"Requested Validity: {self.requested_validity_years} years")
        if self.additional_notes:
            lines.append(f"Notes: {self.additional_notes}")
        return "\n".join(lines)

    def to_summary_bn(self) -> str:
        """Generate a Bangla summary of the applicant profile."""
        lines = [
            f"বয়স: {self.age} বছর ({self.age_category_bn})",
            f"পেশা: {self.profession.label_bn}",
            f"ডেলিভারি ধরন: {self.delivery_type.label_bn}",
            f"পৃষ্ঠা সংখ্যা: {self.page_count.value} পৃষ্ঠা",
            f"জাতীয় পরিচয়পত্র: {'আছে' if self.has_nid else 'নেই'}",
            f"জন্ম নিবন্ধন: {'আছে' if self.has_birth_certificate else 'নেই'}",
            f"জেলা: {self.district}",
        ]
        return "\n".join(lines)
