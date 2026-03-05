"""
Document Checklist Task
Task for the Document Architect agent.
Compiles the final Passport Readiness Report.
"""

from crewai import Agent, Task
from src.models.applicant import ApplicantProfile


def create_checklist_task(
    agent: Agent,
    profile: ApplicantProfile,
    eligibility_task: Task,
    fee_task: Task,
) -> Task:
    """
    Create the document checklist task for the Document Architect.

    This is the THIRD and FINAL task in the pipeline. It receives context
    from both the eligibility and fee tasks to compile the complete report.

    Args:
        agent: The Document Architect agent.
        profile: The applicant's profile.
        eligibility_task: The completed eligibility task.
        fee_task: The completed fee task.

    Returns:
        Configured CrewAI Task instance.
    """
    description = f"""
Generate a customized document checklist and compile the FINAL Passport Readiness Report.

═══════════════════════════════════════════
APPLICANT PROFILE FOR DOCUMENT CHECKLIST
═══════════════════════════════════════════
Age: {profile.age} years
Profession: {profile.profession.value}
Has Name Change: {'Yes' if profile.has_name_change else 'No'}
Is Renewal: {'Yes' if profile.is_renewal else 'No'}
District: {profile.district}
═══════════════════════════════════════════

YOUR TASKS:
1. Use the Document Checklist Lookup Tool with:
   - age = {profile.age}
   - profession = "{profile.profession.value}"
   - has_name_change = {profile.has_name_change}
   - is_renewal = {profile.is_renewal}

2. Organize the documents into:
   - ✅ Mandatory Documents (applicant MUST have these)
   - 📎 Optional/Conditional Documents (may be needed based on circumstances)

3. Review the context from the Policy Guardian and Fee Calculator to compile
   the COMPLETE Passport Readiness Report.

4. Format the FINAL report as a professional Markdown document with tables.

FINAL REPORT MUST INCLUDE:
━━━━━━━━━━━━━━━━━━━━━━━━━
Section 1: Applicant Summary
Section 2: Eligibility Assessment (from Policy Guardian)
Section 3: Fee Breakdown (from Fee Calculator)
Section 4: Document Checklist (your analysis)
Section 5: Important Notes & Warnings
Section 6: Bangla Summary (বাংলা সারসংক্ষেপ)
━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    expected_output = f"""
Generate the COMPLETE Passport Readiness Report in this EXACT Markdown format:

# 🇧🇩 Bangladesh E-Passport Readiness Report

## 📋 Applicant Summary

| Field | Details |
|-------|---------|
| Name/Reference | Applicant |
| Age | {profile.age} years |
| Profession | {profile.profession.label_en} |
| District | {profile.district} |
| Application Type | {{'Renewal' if profile.is_renewal else 'New Passport'}} |

## 🛡️ Eligibility Assessment

| Parameter | Status |
|-----------|--------|
| Age Category | [From Policy Guardian] |
| Passport Validity | [From Policy Guardian] |
| Required Primary ID | [From Policy Guardian] |
| Eligibility Status | [ELIGIBLE / ELIGIBLE WITH CONDITIONS] |

[Include any ⚠️ warnings or flags from the Policy Guardian]

## 💰 Fee Breakdown

| Component | Amount (BDT) |
|-----------|-------------|
| Page Count | {profile.page_count.value} pages |
| Delivery Type | {profile.delivery_type.label_en} |
| Base Fee | [From Fee Calculator] |
| VAT (15%) | [From Fee Calculator] |
| **Total Fee** | **[From Fee Calculator]** |

## 📑 Required Documents

### Mandatory Documents
| # | Document |
|---|----------|
| 1 | [Document 1] |
| 2 | [Document 2] |
[... Generate ALL mandatory documents]

### Optional / Conditional Documents
| # | Document | Condition |
|---|----------|-----------|
| 1 | [Document 1] | [When needed] |
[... Generate ALL optional documents]

## ⚠️ Important Notes & Warnings
- [List any important notes, warnings, or flags]

## 🇧🇩 বাংলা সারসংক্ষেপ (Bangla Summary)

| বিষয় | বিবরণ |
|-------|--------|
| বয়স | {profile.age} বছর |
| পেশা | {profile.profession.label_bn} |
| পাসপোর্ট মেয়াদ | [From Policy Guardian - in Bangla] |
| মোট ফি | [From Fee Calculator] টাকা |
| প্রয়োজনীয় কাগজপত্র | [Key documents in Bangla] |
"""

    return Task(
        description=description.strip(),
        expected_output=expected_output.strip(),
        agent=agent,
        context=[eligibility_task, fee_task],  # Context from both prior tasks
    )
