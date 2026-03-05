"""
Passport Crew Orchestrator
Main orchestration module that assembles agents, tasks, and the crew.
Handles the complete pipeline from applicant profile to readiness report.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from crewai import Crew, Process, LLM

from src.models.applicant import ApplicantProfile
from src.agents.policy_guardian import create_policy_guardian
from src.agents.fee_calculator import create_fee_calculator
from src.agents.document_architect import create_document_architect
from src.tasks.eligibility_task import create_eligibility_task
from src.tasks.fee_task import create_fee_task
from src.tasks.checklist_task import create_checklist_task

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class PassportCrew:
    """
    Main orchestrator for the Bangladesh E-Passport Multi-Agent System.

    Pipeline:
    1. Policy Guardian → Eligibility Assessment
    2. Fee Calculator → Fee Breakdown (uses eligibility as context)
    3. Document Architect → Checklist + Final Report (uses both as context)
    """

    def __init__(
        self,
        verbose: bool = True,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.1,
    ):
        """
        Initialize the Passport Crew.

        Args:
            verbose: Whether to enable verbose agent output.
            llm_provider: LLM provider ('openai' or 'google'). Defaults to env var.
            model_name: Model name. Defaults to env var.
            temperature: LLM temperature (0.0-1.0).
        """
        self.verbose = verbose
        self.temperature = temperature

        # Resolve LLM configuration
        self.llm_provider = llm_provider or os.getenv("LLM_PROVIDER", "google")
        self.model_name = model_name or self._get_default_model()

        # Initialize LLM
        self.llm = self._create_llm()

        logger.info(
            f"PassportCrew initialized: provider={self.llm_provider}, "
            f"model={self.model_name}, temperature={self.temperature}"
        )

    def _get_default_model(self) -> str:
        """Get the default model name based on provider."""
        if self.llm_provider == "openai":
            return os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        elif self.llm_provider == "google":
            return os.getenv("GOOGLE_MODEL_NAME", "gemini/gemini-2.0-flash")
        else:
            return "gemini/gemini-2.0-flash"

    def _create_llm(self) -> LLM:
        """Create the LLM instance based on configuration."""
        try:
            if self.llm_provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not set in environment variables.")
                return LLM(
                    model=self.model_name,
                    api_key=api_key,
                    temperature=self.temperature,
                )
            elif self.llm_provider == "google":
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not set in environment variables.")
                return LLM(
                    model=self.model_name,
                    api_key=api_key,
                    temperature=self.temperature,
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

        except Exception as e:
            logger.error(f"Failed to create LLM: {e}")
            raise

    def run(self, profile: ApplicantProfile) -> str:
        """
        Run the complete passport assessment pipeline.

        Args:
            profile: The applicant's profile.

        Returns:
            The final Passport Readiness Report as a Markdown string.
        """
        logger.info("=" * 60)
        logger.info("🚀 Starting Passport Assessment Pipeline")
        logger.info("=" * 60)
        logger.info(f"Applicant: age={profile.age}, profession={profile.profession.value}")

        providers_to_try = [self.llm_provider]
        if self.llm_provider == "google":
            providers_to_try.append("openai")
        elif self.llm_provider == "openai":
            providers_to_try.append("google")

        last_error = ""

        for provider in providers_to_try:
            try:
                if provider != self.llm_provider:
                    logger.info(f"🔄 Attempting fallback to {provider} provider...")
                    self.llm_provider = provider
                    self.model_name = self._get_default_model()
                    self.llm = self._create_llm()

                # ── Step 1: Create Agents ───────────────────────────────
                logger.info(f"Creating agents (Provider: {self.llm_provider})...")

                policy_guardian = create_policy_guardian(
                    llm=self.llm,
                    verbose=self.verbose,
                )
                fee_calculator = create_fee_calculator(
                    llm=self.llm,
                    verbose=self.verbose,
                )
                document_architect = create_document_architect(
                    llm=self.llm,
                    verbose=self.verbose,
                )

                logger.info("✅ All 3 agents created successfully")

                # ── Step 2: Create Tasks (with delegation chain) ────────
                logger.info("Creating tasks with delegation chain...")

                # Task 1: Eligibility (Policy Guardian)
                eligibility_task = create_eligibility_task(
                    agent=policy_guardian,
                    profile=profile,
                )

                # Task 2: Fee Calculation (receives Task 1 as context)
                fee_task = create_fee_task(
                    agent=fee_calculator,
                    profile=profile,
                    eligibility_task=eligibility_task,
                )

                # Task 3: Document Checklist + Final Report (receives Tasks 1 & 2)
                checklist_task = create_checklist_task(
                    agent=document_architect,
                    profile=profile,
                    eligibility_task=eligibility_task,
                    fee_task=fee_task,
                )

                logger.info("✅ All 3 tasks created with delegation chain")

                # ── Step 3: Assemble and Run the Crew ───────────────────
                logger.info("Assembling the crew...")

                crew = Crew(
                    agents=[policy_guardian, fee_calculator, document_architect],
                    tasks=[eligibility_task, fee_task, checklist_task],
                    process=Process.sequential,
                    verbose=self.verbose,
                )

                logger.info(f"⚡ Kicking off the crew with {self.llm_provider}...")
                result = crew.kickoff()

                logger.info("=" * 60)
                logger.info("✅ Passport Assessment Pipeline COMPLETE")
                logger.info("=" * 60)

                return str(result)

            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ Pipeline failed with provider {provider}: {last_error}")
                
                # Check for rate limit keywords indicating we should try fallback
                error_str = last_error.lower()
                is_rate_limit = any(
                    kw in error_str
                    for kw in ["429", "quota", "rate limit", "ratelimit", "resource_exhausted", "too_many_requests"]
                )
                
                if is_rate_limit and provider == providers_to_try[0] and len(providers_to_try) > 1:
                    logger.warning(f"Rate limit detected for {provider}. Falling back to next available provider...")
                    continue  # Try the next provider
                
                # If it's not a rate limit issue or we've exhausted options, break and use DB fallback
                break

        # Generate fallback report using local database
        return self._generate_fallback_report(profile, f"Provider error: {last_error}")

    def _generate_fallback_report(self, profile: ApplicantProfile, error: str) -> str:
        """
        Generate a fallback report using local database when the LLM pipeline fails.

        Args:
            profile: The applicant's profile.
            error: The error message from the failed pipeline.

        Returns:
            A basic Passport Readiness Report from local data.
        """
        logger.warning("🔄 Generating FALLBACK report from local database...")

        from src.database.policy_rules import PolicyDatabase
        from src.database.fee_structure import FeeDatabase
        from src.database.document_requirements import DocumentDatabase

        # Get policy
        policy = PolicyDatabase.get_policy(profile.age) or {}
        max_validity = PolicyDatabase.get_max_validity(profile.age)

        # Validate requested validity
        validation = None
        if profile.requested_validity_years:
            validation = PolicyDatabase.validate_validity_request(
                profile.age, profile.requested_validity_years
            )

        # Get fee
        fee = FeeDatabase.get_fee(
            profile.page_count.value,
            profile.delivery_type.value,
        ) or {}

        # Get checklist
        checklist_md = DocumentDatabase.get_checklist_markdown(
            age=profile.age,
            profession=profile.profession.value,
            has_name_change=profile.has_name_change,
            is_renewal=profile.is_renewal,
        )

        # Compile the report
        warnings = []
        if validation and validation.get("flag") == "INCONSISTENCY_FLAGGED":
            warnings.append(validation["message"])

        validity_display = f"{max_validity} Years"
        if max_validity != profile.requested_validity_years and profile.requested_validity_years:
            validity_display += f" (Adjusted from requested {profile.requested_validity_years} years)"

        report_lines = [
            "# 🇧🇩 Bangladesh E-Passport Readiness Report",
            "",
            "> ⚠️ **Note**: This report was generated from the local database (fallback mode) "
            f"due to an error: {error}",
            "",
            "## 📋 Applicant Summary",
            "",
            "| Field | Details |",
            "|-------|---------|",
            f"| Age | {profile.age} years ({profile.age_category}) |",
            f"| Profession | {profile.profession.label_en} |",
            f"| District | {profile.district} |",
            f"| Application Type | {'Renewal' if profile.is_renewal else 'New Passport'} |",
            "",
            "## 🛡️ Eligibility Assessment",
            "",
            "| Parameter | Status |",
            "|-----------|--------|",
            f"| Age Category | {profile.age_category.title()} |",
            f"| Passport Validity | {validity_display} |",
            f"| Required Primary ID | {policy.get('required_id_type', 'NID / Birth Certificate')} |",
            f"| Eligibility Status | {'ELIGIBLE' if not warnings else 'ELIGIBLE WITH CONDITIONS'} |",
            "",
        ]

        if warnings:
            report_lines.extend([
                "### ⚠️ Warnings",
                "",
            ])
            for w in warnings:
                report_lines.append(f"- {w}")
            report_lines.append("")

        if fee:
            report_lines.extend([
                "## 💰 Fee Breakdown",
                "",
                "| Component | Amount (BDT) |",
                "|-----------|-------------|",
                f"| Page Count | {profile.page_count.value} pages |",
                f"| Delivery Type | {profile.delivery_type.label_en} |",
                f"| Base Fee | {fee['base_fee']:,.0f} BDT |",
                f"| VAT (15%) | {fee['vat_amount']:,.0f} BDT |",
                f"| **Total Fee** | **{fee['total_fee']:,.0f} BDT** |",
                "",
            ])

        report_lines.extend([
            checklist_md,
            "",
            "## 🇧🇩 বাংলা সারসংক্ষেপ",
            "",
            "| বিষয় | বিবরণ |",
            "|-------|--------|",
            f"| বয়স | {profile.age} বছর ({profile.age_category_bn}) |",
            f"| পেশা | {profile.profession.label_bn} |",
            f"| পাসপোর্ট মেয়াদ | {max_validity} বছর |",
            f"| ডেলিভারি ধরন | {profile.delivery_type.label_bn} |",
            f"| মোট ফি | {fee.get('total_fee', 'N/A'):,.0f} টাকা |" if fee else "| মোট ফি | তথ্য পাওয়া যায়নি |",
            f"| প্রাথমিক পরিচয়পত্র | {policy.get('required_id_type_bn', 'জাতীয় পরিচয়পত্র / জন্ম নিবন্ধন')} |",
            "",
            "---",
            f"*Report generated in fallback mode from local database.*",
        ])

        report = "\n".join(report_lines)
        logger.info("✅ Fallback report generated successfully")
        return report
