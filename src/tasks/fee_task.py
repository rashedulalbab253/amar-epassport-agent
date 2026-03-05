"""
Fee Calculation Task
Task for the Fee Calculator agent.
Receives context from the Eligibility Task.
"""

from crewai import Agent, Task
from src.models.applicant import ApplicantProfile


def create_fee_task(
    agent: Agent,
    profile: ApplicantProfile,
    eligibility_task: Task,
) -> Task:
    """
    Create the fee calculation task for the Fee Calculator.

    This is the SECOND task in the pipeline. It receives the output
    of the eligibility task as context (task delegation).

    Args:
        agent: The Fee Calculator agent.
        profile: The applicant's profile.
        eligibility_task: The completed eligibility task (passed as context).

    Returns:
        Configured CrewAI Task instance.
    """
    description = f"""
Calculate the exact passport fee for this applicant using the 2026 official fee structure.

═══════════════════════════════════════════
APPLICANT DETAILS FOR FEE CALCULATION
═══════════════════════════════════════════
Page Count: {profile.page_count.value} pages
Delivery Type: {profile.delivery_type.value}
Is Renewal: {'Yes' if profile.is_renewal else 'No'}
═══════════════════════════════════════════

YOUR TASKS:
1. Use the Fee Lookup Tool with:
   - page_count = {profile.page_count.value}
   - delivery_type = "{profile.delivery_type.value}"

2. Present the fee breakdown:
   - Base Fee (before VAT)
   - VAT Amount (15%)
   - Total Fee (Base + VAT)

3. Review the Policy Guardian's eligibility assessment from context to ensure
   the fee calculation aligns with the approved validity period.

4. If the applicant's delivery type is 'express' or 'super_express', make sure
   to highlight the premium they are paying compared to regular delivery.

IMPORTANT: 
- All amounts must be in BDT (Bangladeshi Taka)
- VAT rate is exactly 15%
- Use the 2026 official fee structure ONLY
"""

    expected_output = """
Provide a detailed fee calculation with these fields:
1. **Page Count**: (48 or 64 pages)
2. **Delivery Type**: (Regular / Express / Super Express)
3. **Base Fee**: [Amount] BDT
4. **VAT (15%)**: [Amount] BDT
5. **Total Fee**: [Amount] BDT
6. **Fee Comparison** (if express/super express): Show how much more vs regular
7. **Payment Notes**: Any relevant payment instructions
"""

    return Task(
        description=description.strip(),
        expected_output=expected_output.strip(),
        agent=agent,
        context=[eligibility_task],  # Task delegation from Policy Guardian
    )
