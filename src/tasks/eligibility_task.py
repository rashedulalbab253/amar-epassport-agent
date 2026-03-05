"""
Eligibility Assessment Task
Task for the Policy Guardian agent to determine passport eligibility.
"""

from crewai import Agent, Task
from src.models.applicant import ApplicantProfile


def create_eligibility_task(
    agent: Agent,
    profile: ApplicantProfile,
) -> Task:
    """
    Create the eligibility assessment task for the Policy Guardian.

    This is the FIRST task in the pipeline. Its output is passed as
    context to the Fee Calculator task.

    Args:
        agent: The Policy Guardian agent.
        profile: The applicant's profile.

    Returns:
        Configured CrewAI Task instance.
    """
    # Build the validity validation portion
    validity_note = ""
    if profile.requested_validity_years:
        validity_note = (
            f"\n\n⚠️ IMPORTANT: The applicant has specifically requested a "
            f"{profile.requested_validity_years}-year passport. You MUST validate whether "
            f"this is permitted for their age ({profile.age} years). If NOT permitted, "
            f"FLAG the inconsistency clearly and state the corrected validity period."
        )

    description = f"""
Analyze the following passport applicant's eligibility based on Bangladesh E-Passport policies.

═══════════════════════════════════════════
APPLICANT PROFILE
═══════════════════════════════════════════
{profile.to_summary()}
═══════════════════════════════════════════

YOUR TASKS:
1. Use the Policy Lookup Tool with the applicant's age ({profile.age}) to determine:
   - Permitted passport validity period(s)
   - Required primary identification document
   - Any age-based restrictions

2. {'Use the Validate Validity Request Tool to check if the requested ' + str(profile.requested_validity_years) + '-year validity is permitted for age ' + str(profile.age) + '.' if profile.requested_validity_years else 'Determine the recommended validity period for this applicant.'}

3. Check if the applicant's submitted documents match what is required:
   - Has NID: {'Yes' if profile.has_nid else 'No'}
   - Has Birth Certificate: {'Yes' if profile.has_birth_certificate else 'No'}
{validity_note}

IMPORTANT RULES:
- Under 18 → 5-year ONLY, Birth Registration Certificate required, Parent's NID needed
- 18-65 → 5 or 10 years allowed, NID (Smart Card) required
- Over 65 → 5-year ONLY, NID required
- If ANY inconsistency exists, FLAG IT clearly with ⚠️
"""

    expected_output = """
Provide a structured eligibility assessment with these fields:
1. **Age Category**: (Minor / Adult / Senior)
2. **Permitted Validity**: (5 years / 5 or 10 years)
3. **Recommended Validity**: (the optimal choice for this applicant)
4. **Required Primary ID**: (NID or Birth Registration Certificate)
5. **ID Document Status**: (Verified / Missing — with details)
6. **Restrictions**: (list any that apply)
7. **Flags/Warnings**: (any inconsistencies found)
8. **Eligibility Status**: (ELIGIBLE / ELIGIBLE WITH CONDITIONS / INELIGIBLE)
"""

    return Task(
        description=description.strip(),
        expected_output=expected_output.strip(),
        agent=agent,
    )
