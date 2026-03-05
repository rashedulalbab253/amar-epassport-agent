"""
Unit Tests for Local Database Modules
Tests fee structure, policy rules, and document requirements.
"""

import pytest
from src.database.fee_structure import FeeDatabase, FeeEntry
from src.database.policy_rules import PolicyDatabase
from src.database.document_requirements import DocumentDatabase


class TestFeeEntry:
    """Tests for FeeEntry dataclass."""

    def test_vat_calculation(self):
        entry = FeeEntry(base_fee=3450.00)
        assert entry.vat_rate == 0.15
        assert entry.vat_amount == 517.50
        assert entry.total_fee == 3967.50

    def test_custom_vat_rate(self):
        entry = FeeEntry(base_fee=1000.00, vat_rate=0.10)
        assert entry.vat_amount == 100.00
        assert entry.total_fee == 1100.00


class TestFeeDatabase:
    """Tests for FeeDatabase."""

    def test_regular_48_page_fee(self):
        result = FeeDatabase.get_fee(48, "regular")
        assert result is not None
        assert result["base_fee"] == 3450.00
        assert result["total_fee"] == 3967.50
        assert result["currency"] == "BDT"

    def test_express_64_page_fee(self):
        result = FeeDatabase.get_fee(64, "express")
        assert result is not None
        assert result["base_fee"] == 8625.00

    def test_super_express_48_fee(self):
        result = FeeDatabase.get_fee(48, "super_express")
        assert result is not None
        assert result["base_fee"] == 8625.00

    def test_super_express_64_fee(self):
        result = FeeDatabase.get_fee(64, "super_express")
        assert result is not None
        assert result["base_fee"] == 11500.00

    def test_invalid_page_count(self):
        result = FeeDatabase.get_fee(32, "regular")
        assert result is None

    def test_invalid_delivery_type(self):
        result = FeeDatabase.get_fee(48, "overnight")
        assert result is None

    def test_vat_is_15_percent(self):
        result = FeeDatabase.get_fee(48, "regular")
        expected_vat = 3450.00 * 0.15
        assert abs(result["vat_amount"] - expected_vat) < 0.01

    def test_fee_table_generation(self):
        table = FeeDatabase.get_fee_table()
        assert "Fee Structure" in table
        assert "BDT" in table or "48" in table
        assert "Regular" in table
        assert "Express" in table

    def test_additional_fee_lost_passport(self):
        result = FeeDatabase.get_additional_fee("lost_passport_penalty")
        assert result is not None
        assert result["base_fee"] == 15000.00

    def test_additional_fee_invalid(self):
        result = FeeDatabase.get_additional_fee("nonexistent")
        assert result is None


class TestPolicyDatabase:
    """Tests for PolicyDatabase."""

    def test_age_category_minor(self):
        assert PolicyDatabase.get_age_category(5) == "minor"
        assert PolicyDatabase.get_age_category(17) == "minor"

    def test_age_category_adult(self):
        assert PolicyDatabase.get_age_category(18) == "adult"
        assert PolicyDatabase.get_age_category(40) == "adult"
        assert PolicyDatabase.get_age_category(65) == "adult"

    def test_age_category_senior(self):
        assert PolicyDatabase.get_age_category(66) == "senior"
        assert PolicyDatabase.get_age_category(80) == "senior"

    def test_minor_policy(self):
        policy = PolicyDatabase.get_policy(15)
        assert policy is not None
        assert policy["age_category"] == "minor"
        assert policy["allowed_validity_years"] == [5]
        assert "Birth" in policy["required_id_type"]

    def test_adult_policy(self):
        policy = PolicyDatabase.get_policy(30)
        assert policy is not None
        assert policy["age_category"] == "adult"
        assert 5 in policy["allowed_validity_years"]
        assert 10 in policy["allowed_validity_years"]
        assert "NID" in policy["required_id_type"]

    def test_senior_policy(self):
        policy = PolicyDatabase.get_policy(70)
        assert policy is not None
        assert policy["age_category"] == "senior"
        assert policy["allowed_validity_years"] == [5]

    def test_minor_requesting_10_year_flagged(self):
        """Critical test: 15-year-old requesting 10-year passport should be flagged."""
        result = PolicyDatabase.validate_validity_request(15, 10)
        assert result["valid"] is False
        assert result["flag"] == "INCONSISTENCY_FLAGGED"
        assert result["corrected_validity"] == 5

    def test_adult_requesting_10_year_valid(self):
        result = PolicyDatabase.validate_validity_request(30, 10)
        assert result["valid"] is True
        assert result["flag"] is None

    def test_adult_requesting_5_year_valid(self):
        result = PolicyDatabase.validate_validity_request(30, 5)
        assert result["valid"] is True

    def test_senior_requesting_10_year_flagged(self):
        result = PolicyDatabase.validate_validity_request(70, 10)
        assert result["valid"] is False
        assert result["flag"] == "INCONSISTENCY_FLAGGED"

    def test_max_validity_minor(self):
        assert PolicyDatabase.get_max_validity(15) == 5

    def test_max_validity_adult(self):
        assert PolicyDatabase.get_max_validity(30) == 10

    def test_max_validity_senior(self):
        assert PolicyDatabase.get_max_validity(70) == 5


class TestDocumentDatabase:
    """Tests for DocumentDatabase."""

    def test_adult_private_sector_checklist(self):
        result = DocumentDatabase.get_checklist(24, "private_sector")
        assert result is not None
        assert result["age_category"] == "adult"
        assert result["total_mandatory"] > 0

        # Should contain NID for adults
        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("NID" in name or "National ID" in name for name in doc_names)

        # Should contain employment certificate
        assert any("Employment" in name or "Employer" in name for name in doc_names)

    def test_minor_checklist_has_parent_nid(self):
        result = DocumentDatabase.get_checklist(10, "minor")
        assert result is not None
        assert result["age_category"] == "minor"

        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("Parent" in name for name in doc_names)

    def test_government_employee_has_noc(self):
        result = DocumentDatabase.get_checklist(35, "government")
        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("GO" in name or "NOC" in name for name in doc_names)

    def test_business_has_trade_license(self):
        result = DocumentDatabase.get_checklist(40, "business")
        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("Trade License" in name for name in doc_names)

    def test_name_change_has_gazette(self):
        result = DocumentDatabase.get_checklist(30, "private_sector", has_name_change=True)
        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("Gazette" in name for name in doc_names)
        assert any("Marriage" in name for name in doc_names)

    def test_renewal_has_old_passport(self):
        result = DocumentDatabase.get_checklist(30, "private_sector", is_renewal=True)
        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("Previous Passport" in name for name in doc_names)

    def test_universal_documents_always_included(self):
        result = DocumentDatabase.get_checklist(30, "other")
        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("Application Form" in name for name in doc_names)
        assert any("Photograph" in name for name in doc_names)

    def test_markdown_generation(self):
        md = DocumentDatabase.get_checklist_markdown(24, "private_sector")
        assert "Required Documents" in md
        assert "|" in md  # Should contain table format

    def test_housewife_has_marriage_cert(self):
        result = DocumentDatabase.get_checklist(30, "housewife")
        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("Marriage" in name or "Nikah" in name for name in doc_names)
        assert any("Husband" in name for name in doc_names)

    def test_doctor_has_bmdc(self):
        result = DocumentDatabase.get_checklist(30, "doctor")
        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("BMDC" in name for name in doc_names)

    def test_student_has_student_id(self):
        result = DocumentDatabase.get_checklist(20, "student")
        doc_names = [d["name_en"] for d in result["mandatory_documents"]]
        assert any("Student" in name for name in doc_names)
