"""
Document Checklist Lookup Tool for CrewAI Agents
Wraps the local DocumentDatabase for use by the Document Architect agent.
Includes fallback handling for reliable operation.
"""

import json
import logging
from crewai.tools import tool
from src.database.document_requirements import DocumentDatabase

logger = logging.getLogger(__name__)


@tool("Document Checklist Lookup Tool")
def document_checklist_lookup(
    age: int,
    profession: str,
    has_name_change: bool = False,
    is_renewal: bool = False,
) -> str:
    """
    Generate a customized document checklist for a Bangladesh E-Passport application.
    The checklist is tailored based on age, profession, and special circumstances.

    Args:
        age: The applicant's age in years.
        profession: The applicant's profession. Must be one of: 'government', 'private_sector',
                    'business', 'student', 'doctor', 'engineer', 'lawyer', 'teacher',
                    'housewife', 'unemployed', 'retired', 'minor', 'other'.
        has_name_change: Whether the applicant has a name change (default: False).
        is_renewal: Whether this is a passport renewal (default: False).

    Returns:
        JSON string with categorized mandatory and optional document lists.
    """
    try:
        logger.info(
            f"Generating checklist: age={age}, profession={profession}, "
            f"name_change={has_name_change}, renewal={is_renewal}"
        )

        # Normalize profession
        profession = profession.lower().strip().replace(" ", "_")

        result = DocumentDatabase.get_checklist(
            age=age,
            profession=profession,
            has_name_change=has_name_change,
            is_renewal=is_renewal,
        )

        logger.info(
            f"Checklist generated: {result['total_mandatory']} mandatory, "
            f"{result['total_optional']} optional documents"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error generating document checklist: {e}")
        # Provide a minimal fallback checklist
        return json.dumps({
            "error": True,
            "message": f"Error generating checklist: {str(e)}. Providing basic checklist.",
            "fallback": True,
            "mandatory_documents": [
                {"name_en": "National ID Card (NID) or Birth Registration Certificate", "name_bn": "জাতীয় পরিচয়পত্র (NID) বা জন্ম নিবন্ধন সনদ"},
                {"name_en": "Completed Application Form", "name_bn": "পূরণকৃত আবেদন ফর্ম"},
                {"name_en": "Passport-Size Photographs", "name_bn": "পাসপোর্ট সাইজ ছবি"},
                {"name_en": "Bank Payment Receipt", "name_bn": "ব্যাংক পেমেন্ট রসিদ"},
            ],
            "optional_documents": [],
            "source": "Fallback — Error Recovery",
        }, indent=2, ensure_ascii=False)
