"""
Bangladesh E-Passport Document Requirements Database
Local fallback data source for document checklist generation.
Customized based on profession, age, and special circumstances.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DocumentItem:
    """Represents a single required document."""
    name_en: str
    name_bn: str
    is_mandatory: bool = True
    notes_en: str = ""
    notes_bn: str = ""


class DocumentDatabase:
    """
    Local database of document requirements for Bangladesh E-Passport applications.
    Generates customized checklists based on applicant profile.
    """

    # ─────────────────────────────────────────────────────────────
    # Universal Documents (required for ALL applicants)
    # ─────────────────────────────────────────────────────────────
    UNIVERSAL_DOCUMENTS: List[DocumentItem] = [
        DocumentItem(
            name_en="Completed Online Application Form (MRP/E-Passport Form)",
            name_bn="পূরণকৃত অনলাইন আবেদন ফর্ম (MRP/ই-পাসপোর্ট ফর্ম)",
        ),
        DocumentItem(
            name_en="Recent Passport-Size Photographs (Digital & Physical)",
            name_bn="সাম্প্রতিক পাসপোর্ট সাইজ ছবি (ডিজিটাল ও প্রিন্ট)",
            notes_en="White background, 45mm x 35mm, matte finish",
            notes_bn="সাদা ব্যাকগ্রাউন্ড, ৪৫মিমি x ৩৫মিমি, ম্যাট ফিনিশ",
        ),
        DocumentItem(
            name_en="Birth Registration Certificate",
            name_bn="জন্ম নিবন্ধন সনদ",
        ),
        DocumentItem(
            name_en="Bank Payment Receipt / Treasury Challan",
            name_bn="ব্যাংক পেমেন্ট রসিদ / ট্রেজারি চালান",
        ),
    ]

    # ─────────────────────────────────────────────────────────────
    # Age-Specific Documents
    # ─────────────────────────────────────────────────────────────
    AGE_DOCUMENTS: Dict[str, List[DocumentItem]] = {
        "minor": [
            DocumentItem(
                name_en="Parent's/Guardian's National ID Card (NID) — Both Parents",
                name_bn="পিতা/মাতা/অভিভাবকের জাতীয় পরিচয়পত্র (NID) — উভয় পিতামাতা",
            ),
            DocumentItem(
                name_en="Parent's/Guardian's Passport Copy (if available)",
                name_bn="পিতা/মাতা/অভিভাবকের পাসপোর্ট কপি (থাকলে)",
                is_mandatory=False,
            ),
            DocumentItem(
                name_en="Parent's Consent Letter / Affidavit",
                name_bn="পিতা/মাতার সম্মতিপত্র / হলফনামা",
            ),
            DocumentItem(
                name_en="School/Institution Student ID or Certificate",
                name_bn="স্কুল/প্রতিষ্ঠানের শিক্ষার্থী পরিচয়পত্র বা সনদ",
                is_mandatory=False,
                notes_en="Required if applicant is a student",
                notes_bn="শিক্ষার্থী হলে প্রয়োজন",
            ),
            DocumentItem(
                name_en="Court Order (if parents are divorced/separated)",
                name_bn="আদালতের আদেশ (পিতামাতা বিবাহবিচ্ছেদ/পৃথক হলে)",
                is_mandatory=False,
                notes_en="Only required if applicable",
                notes_bn="প্রযোজ্য হলে প্রয়োজন",
            ),
        ],
        "adult": [
            DocumentItem(
                name_en="National ID Card (NID / Smart Card)",
                name_bn="জাতীয় পরিচয়পত্র (NID / স্মার্ট কার্ড)",
            ),
        ],
        "senior": [
            DocumentItem(
                name_en="National ID Card (NID / Smart Card)",
                name_bn="জাতীয় পরিচয়পত্র (NID / স্মার্ট কার্ড)",
            ),
            DocumentItem(
                name_en="Medical Fitness Certificate (if required)",
                name_bn="চিকিৎসা সক্ষমতা সনদ (প্রয়োজন হলে)",
                is_mandatory=False,
            ),
        ],
    }

    # ─────────────────────────────────────────────────────────────
    # Profession-Specific Documents
    # ─────────────────────────────────────────────────────────────
    PROFESSION_DOCUMENTS: Dict[str, List[DocumentItem]] = {
        "government": [
            DocumentItem(
                name_en="Government Order (GO) / No Objection Certificate (NOC)",
                name_bn="সরকারি আদেশ (GO) / অনাপত্তি সনদ (NOC)",
                notes_en="Must be issued by the employing ministry/department",
                notes_bn="নিয়োগকারী মন্ত্রণালয়/বিভাগ কর্তৃক জারি করতে হবে",
            ),
            DocumentItem(
                name_en="Service ID Card",
                name_bn="সার্ভিস আইডি কার্ড",
            ),
            DocumentItem(
                name_en="Last Pay Certificate / Pay Slip",
                name_bn="সর্বশেষ বেতন সনদ / বেতন স্লিপ",
                is_mandatory=False,
            ),
        ],
        "private_sector": [
            DocumentItem(
                name_en="Employment Certificate from Employer",
                name_bn="নিয়োগকর্তার নিয়োগ সনদ",
            ),
            DocumentItem(
                name_en="Employee ID Card",
                name_bn="কর্মচারী পরিচয়পত্র",
                is_mandatory=False,
            ),
            DocumentItem(
                name_en="Company Trade License Copy",
                name_bn="কোম্পানি ট্রেড লাইসেন্স কপি",
                is_mandatory=False,
            ),
        ],
        "business": [
            DocumentItem(
                name_en="Trade License (Valid/Updated)",
                name_bn="ট্রেড লাইসেন্স (বৈধ/হালনাগাদ)",
            ),
            DocumentItem(
                name_en="TIN Certificate",
                name_bn="টিআইএন সনদ",
            ),
            DocumentItem(
                name_en="Company Registration Certificate (if applicable)",
                name_bn="কোম্পানি নিবন্ধন সনদ (প্রযোজ্য হলে)",
                is_mandatory=False,
            ),
        ],
        "student": [
            DocumentItem(
                name_en="Student ID Card (Current Institution)",
                name_bn="শিক্ষার্থী পরিচয়পত্র (বর্তমান প্রতিষ্ঠান)",
            ),
            DocumentItem(
                name_en="Institution's Bonafide Certificate / Enrollment Letter",
                name_bn="প্রতিষ্ঠানের বোনাফাইড সনদ / ভর্তি পত্র",
            ),
            DocumentItem(
                name_en="Latest Academic Certificate or Marksheet",
                name_bn="সর্বশেষ একাডেমিক সনদ বা মার্কশিট",
                is_mandatory=False,
            ),
        ],
        "doctor": [
            DocumentItem(
                name_en="BMDC Registration Certificate",
                name_bn="BMDC নিবন্ধন সনদ",
                notes_en="Bangladesh Medical & Dental Council Registration",
                notes_bn="বাংলাদেশ মেডিকেল ও ডেন্টাল কাউন্সিল নিবন্ধন",
            ),
            DocumentItem(
                name_en="Medical Degree Certificate",
                name_bn="চিকিৎসা ডিগ্রি সনদ",
            ),
        ],
        "engineer": [
            DocumentItem(
                name_en="IEB Membership Certificate",
                name_bn="IEB সদস্যপদ সনদ",
                notes_en="Institution of Engineers, Bangladesh",
                notes_bn="ইনস্টিটিউশন অব ইঞ্জিনিয়ার্স, বাংলাদেশ",
            ),
            DocumentItem(
                name_en="Engineering Degree Certificate",
                name_bn="প্রকৌশল ডিগ্রি সনদ",
            ),
        ],
        "lawyer": [
            DocumentItem(
                name_en="Bar Council Enrollment Certificate",
                name_bn="বার কাউন্সিল তালিকাভুক্তি সনদ",
            ),
            DocumentItem(
                name_en="Law Degree Certificate",
                name_bn="আইন ডিগ্রি সনদ",
            ),
        ],
        "teacher": [
            DocumentItem(
                name_en="MPO Sheet / Employment Letter from Institution",
                name_bn="MPO শিট / প্রতিষ্ঠানের নিয়োগ পত্র",
            ),
            DocumentItem(
                name_en="Teacher Registration Certificate (NTRCA — if applicable)",
                name_bn="শিক্ষক নিবন্ধন সনদ (NTRCA — প্রযোজ্য হলে)",
                is_mandatory=False,
            ),
        ],
        "housewife": [
            DocumentItem(
                name_en="Husband's NID Card Copy",
                name_bn="স্বামীর জাতীয় পরিচয়পত্রের কপি",
            ),
            DocumentItem(
                name_en="Marriage Certificate (Nikah Nama / Kabinnama)",
                name_bn="বিবাহ সনদ (নিকাহনামা / কাবিননামা)",
            ),
        ],
        "unemployed": [
            DocumentItem(
                name_en="Self-Declaration / Affidavit of Unemployment",
                name_bn="স্ব-ঘোষণা / বেকারত্বের হলফনামা",
                notes_en="Notarized declaration on non-judicial stamp paper",
                notes_bn="নন-জুডিশিয়াল স্ট্যাম্প পেপারে নোটারাইজড ঘোষণা",
            ),
        ],
        "retired": [
            DocumentItem(
                name_en="Retirement Order / Pension Book",
                name_bn="অবসর আদেশ / পেনশন বই",
            ),
            DocumentItem(
                name_en="Previous Service ID (if available)",
                name_bn="পূর্ববর্তী সার্ভিস আইডি (থাকলে)",
                is_mandatory=False,
            ),
        ],
        "minor": [],  # Handled by age-specific documents
        "other": [
            DocumentItem(
                name_en="Self-Declaration / Affidavit of Profession",
                name_bn="পেশার স্ব-ঘোষণা / হলফনামা",
            ),
        ],
    }

    # ─────────────────────────────────────────────────────────────
    # Special Circumstance Documents
    # ─────────────────────────────────────────────────────────────
    SPECIAL_DOCUMENTS: Dict[str, List[DocumentItem]] = {
        "name_change": [
            DocumentItem(
                name_en="Marriage Certificate (Nikah Nama / Kabinnama)",
                name_bn="বিবাহ সনদ (নিকাহনামা / কাবিননামা)",
            ),
            DocumentItem(
                name_en="Gazette Notification of Name Change",
                name_bn="নাম পরিবর্তনের গেজেট বিজ্ঞপ্তি",
            ),
            DocumentItem(
                name_en="Affidavit for Name Change (Notarized)",
                name_bn="নাম পরিবর্তনের হলফনামা (নোটারাইজড)",
            ),
        ],
        "renewal": [
            DocumentItem(
                name_en="Previous Passport (Original + Photocopy of all pages)",
                name_bn="পূর্ববর্তী পাসপোর্ট (মূল + সকল পৃষ্ঠার ফটোকপি)",
            ),
        ],
        "lost_passport": [
            DocumentItem(
                name_en="General Diary (GD) from Police Station",
                name_bn="পুলিশ স্টেশন থেকে সাধারণ ডায়েরি (GD)",
            ),
            DocumentItem(
                name_en="Newspaper Advertisement (Lost Passport Notice)",
                name_bn="পত্রিকায় বিজ্ঞাপন (পাসপোর্ট হারানোর বিজ্ঞপ্তি)",
            ),
            DocumentItem(
                name_en="Previous Passport Number and Details",
                name_bn="পূর্ববর্তী পাসপোর্ট নম্বর ও বিবরণ",
            ),
        ],
    }

    @classmethod
    def get_checklist(
        cls,
        age: int,
        profession: str,
        has_name_change: bool = False,
        is_renewal: bool = False,
    ) -> Dict:
        """
        Generate a customized document checklist based on applicant profile.

        Args:
            age: Applicant's age
            profession: Applicant's profession category
            has_name_change: Whether the applicant has a name change
            is_renewal: Whether this is a passport renewal

        Returns:
            Dictionary with categorized document checklist.
        """
        # Determine age category
        if age < 18:
            age_category = "minor"
        elif age > 65:
            age_category = "senior"
        else:
            age_category = "adult"

        # Collect all documents
        mandatory_docs = []
        optional_docs = []

        # 1. Universal documents
        for doc in cls.UNIVERSAL_DOCUMENTS:
            if doc.is_mandatory:
                mandatory_docs.append(doc)
            else:
                optional_docs.append(doc)

        # 2. Age-specific documents
        age_docs = cls.AGE_DOCUMENTS.get(age_category, [])
        for doc in age_docs:
            if doc.is_mandatory:
                mandatory_docs.append(doc)
            else:
                optional_docs.append(doc)

        # 3. Profession-specific documents
        prof_docs = cls.PROFESSION_DOCUMENTS.get(profession, [])
        for doc in prof_docs:
            if doc.is_mandatory:
                mandatory_docs.append(doc)
            else:
                optional_docs.append(doc)

        # 4. Special circumstance documents
        if has_name_change:
            for doc in cls.SPECIAL_DOCUMENTS.get("name_change", []):
                mandatory_docs.append(doc)

        if is_renewal:
            for doc in cls.SPECIAL_DOCUMENTS.get("renewal", []):
                mandatory_docs.append(doc)

        return {
            "age_category": age_category,
            "profession": profession,
            "mandatory_documents": [
                {
                    "name_en": d.name_en,
                    "name_bn": d.name_bn,
                    "notes_en": d.notes_en,
                    "notes_bn": d.notes_bn,
                }
                for d in mandatory_docs
            ],
            "optional_documents": [
                {
                    "name_en": d.name_en,
                    "name_bn": d.name_bn,
                    "notes_en": d.notes_en,
                    "notes_bn": d.notes_bn,
                }
                for d in optional_docs
            ],
            "total_mandatory": len(mandatory_docs),
            "total_optional": len(optional_docs),
            "source": "Local Database — Bangladesh E-Passport Document Requirements",
        }

    @classmethod
    def get_checklist_markdown(
        cls,
        age: int,
        profession: str,
        has_name_change: bool = False,
        is_renewal: bool = False,
    ) -> str:
        """Generate checklist in Markdown format."""
        checklist = cls.get_checklist(age, profession, has_name_change, is_renewal)

        lines = [
            "## 📋 Required Documents Checklist",
            "",
            "### Mandatory Documents",
            "",
            "| # | Document (English) | Document (বাংলা) | Notes |",
            "|---|-------------------|-----------------|-------|",
        ]

        for i, doc in enumerate(checklist["mandatory_documents"], 1):
            notes = doc["notes_en"] if doc["notes_en"] else "—"
            lines.append(f"| {i} | {doc['name_en']} | {doc['name_bn']} | {notes} |")

        if checklist["optional_documents"]:
            lines.extend([
                "",
                "### Optional / Conditional Documents",
                "",
                "| # | Document (English) | Document (বাংলা) | Notes |",
                "|---|-------------------|-----------------|-------|",
            ])
            for i, doc in enumerate(checklist["optional_documents"], 1):
                notes = doc["notes_en"] if doc["notes_en"] else "—"
                lines.append(f"| {i} | {doc['name_en']} | {doc['name_bn']} | {notes} |")

        return "\n".join(lines)
