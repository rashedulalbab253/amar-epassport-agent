"""
Policy Lookup Tool for CrewAI Agents
Wraps the local PolicyDatabase for use by the Policy Guardian agent.
Includes fallback handling for reliable operation.
"""

import json
import logging
from crewai.tools import tool
from src.database.policy_rules import PolicyDatabase

logger = logging.getLogger(__name__)


@tool("Policy Lookup Tool")
def policy_lookup(age: int) -> str:
    """
    Look up Bangladesh E-Passport policy rules based on the applicant's age.
    Returns eligibility details including: allowed validity periods,
    required identification type, additional requirements, and restrictions.

    Args:
        age: The applicant's age in years (integer between 0 and 120).

    Returns:
        JSON string with policy details for the given age.
    """
    try:
        logger.info(f"Looking up policy for age: {age}")

        result = PolicyDatabase.get_policy(age)

        if result is None:
            logger.warning(f"No policy found for age: {age}")
            return json.dumps({
                "error": True,
                "message": f"No policy data available for age {age}. Please verify the age.",
            }, indent=2)

        logger.info(f"Policy found for age {age}: category={result['age_category']}")
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in policy lookup: {e}")
        # Fallback: return the most restrictive policy
        return json.dumps({
            "error": True,
            "message": f"Error looking up policy: {str(e)}. Falling back to default policy.",
            "fallback": True,
            "allowed_validity_years": [5],
            "required_id_type": "National ID Card (NID) or Birth Registration Certificate",
            "notes": "Fallback data — please verify with official sources.",
            "source": "Fallback — Error Recovery",
        }, indent=2, ensure_ascii=False)


@tool("Validate Validity Request Tool")
def validate_validity_request(age: int, requested_validity_years: int) -> str:
    """
    Validate whether a requested passport validity period is allowed for the given age.
    Flags inconsistencies such as a minor requesting a 10-year passport.

    Args:
        age: The applicant's age in years.
        requested_validity_years: The requested passport validity (5 or 10 years).

    Returns:
        JSON string with validation result, any flags/warnings, and corrected validity if needed.
    """
    try:
        logger.info(f"Validating validity request: age={age}, requested={requested_validity_years} years")

        result = PolicyDatabase.validate_validity_request(age, requested_validity_years)

        if result.get("flag") == "INCONSISTENCY_FLAGGED":
            logger.warning(
                f"INCONSISTENCY FLAGGED: {age}-year-old requesting "
                f"{requested_validity_years}-year passport"
            )

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error validating validity request: {e}")
        return json.dumps({
            "valid": False,
            "flag": "ERROR",
            "message": f"Error during validation: {str(e)}. Defaulting to 5-year validity.",
            "corrected_validity": 5,
        }, indent=2, ensure_ascii=False)
