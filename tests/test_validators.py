"""
Unit Tests for Input Validators and Parsers
Tests natural language parsing of applicant profiles.
"""

import pytest
from src.utils.validators import (
    extract_age,
    extract_profession,
    extract_delivery_type,
    extract_page_count,
    extract_has_nid,
    extract_district,
    parse_user_input,
)


class TestExtractAge:
    """Tests for age extraction from natural language."""

    def test_year_old_pattern(self):
        assert extract_age("I am a 24-year-old engineer") == 24

    def test_year_old_no_hyphen(self):
        assert extract_age("I am a 30 year old doctor") == 30

    def test_age_prefix(self):
        assert extract_age("age: 45") == 45
        assert extract_age("Age 50") == 50

    def test_i_am_pattern(self):
        assert extract_age("I am 18") == 18

    def test_no_age(self):
        assert extract_age("I need a passport") is None

    def test_bangla_age(self):
        assert extract_age("আমি 25 বছর") == 25


class TestExtractProfession:
    """Tests for profession extraction."""

    def test_government(self):
        assert extract_profession("I am a government employee") == "government"

    def test_private(self):
        assert extract_profession("I work in private sector") == "private_sector"

    def test_business(self):
        assert extract_profession("I am a business owner") == "business"

    def test_student(self):
        assert extract_profession("I am a university student") == "student"

    def test_doctor(self):
        assert extract_profession("I am a doctor") == "doctor"

    def test_no_profession(self):
        assert extract_profession("I need a passport") is None


class TestExtractDeliveryType:
    """Tests for delivery type extraction."""

    def test_urgent(self):
        assert extract_delivery_type("I need it urgently") == "express"

    def test_express(self):
        assert extract_delivery_type("express delivery") == "express"

    def test_super_express(self):
        assert extract_delivery_type("super express please") == "super_express"

    def test_regular(self):
        assert extract_delivery_type("regular delivery is fine") == "regular"

    def test_no_delivery(self):
        assert extract_delivery_type("I need a passport") is None


class TestExtractPageCount:
    """Tests for page count extraction."""

    def test_64_pages(self):
        assert extract_page_count("I need a 64-page passport") == 64

    def test_48_pages(self):
        assert extract_page_count("48 page passport") == 48

    def test_no_page_count(self):
        assert extract_page_count("I need a passport") is None


class TestExtractNid:
    """Tests for NID detection."""

    def test_has_nid(self):
        assert extract_has_nid("I have an NID") is True

    def test_has_national_id(self):
        assert extract_has_nid("I have my national id") is True

    def test_no_nid_mention(self):
        assert extract_has_nid("I need a passport") is None


class TestExtractDistrict:
    """Tests for district extraction."""

    def test_dhaka(self):
        assert extract_district("I live in Dhaka") == "Dhaka"

    def test_chittagong(self):
        assert extract_district("I am from Chittagong") == "Chittagong"

    def test_no_district(self):
        assert extract_district("I need a passport") is None


class TestParseUserInput:
    """Tests for full user input parsing."""

    def test_example_scenario(self):
        """Test the example scenario from the requirements."""
        text = (
            "I am a 24-year-old private sector employee. I need a 64-page "
            "passport urgently because I have a business trip in two weeks. "
            "I have an NID and I live in Dhaka."
        )
        profile = parse_user_input(text)
        assert profile.age == 24
        assert profile.profession.value == "private_sector"
        assert profile.delivery_type.value == "express"
        assert profile.page_count.value == 64
        assert profile.has_nid is True
        assert profile.district == "Dhaka"

    def test_minor_auto_profession(self):
        """Minors should get profession set to 'minor' automatically."""
        text = "I am a 10-year-old, I need a passport"
        profile = parse_user_input(text)
        assert profile.age == 10
        assert profile.profession.value == "minor"

    def test_missing_age_raises_error(self):
        """Should raise ValueError if age cannot be determined."""
        with pytest.raises(ValueError, match="age"):
            parse_user_input("I need a passport urgently")

    def test_defaults_applied(self):
        """Test that defaults are applied for missing fields."""
        text = "I am 30 years old"
        profile = parse_user_input(text)
        assert profile.delivery_type.value == "regular"  # Default
        assert profile.page_count.value == 48  # Default
        assert profile.district == "Dhaka"  # Default

    def test_name_change_detection(self):
        text = "I am a 30-year-old and I have a name change"
        profile = parse_user_input(text)
        assert profile.has_name_change is True

    def test_renewal_detection(self):
        text = "I am 40 years old and I need a renewal"
        profile = parse_user_input(text)
        assert profile.is_renewal is True
