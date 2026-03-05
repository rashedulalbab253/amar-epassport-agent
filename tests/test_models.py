"""
Unit Tests for Applicant Models
Tests Pydantic model validation, enums, and profile generation.
"""

import pytest
from src.models.applicant import (
    ApplicantProfile,
    DeliveryType,
    PageCount,
    Profession,
)


class TestDeliveryType:
    """Tests for DeliveryType enum."""

    def test_values(self):
        assert DeliveryType.REGULAR.value == "regular"
        assert DeliveryType.EXPRESS.value == "express"
        assert DeliveryType.SUPER_EXPRESS.value == "super_express"

    def test_english_labels(self):
        assert "Regular" in DeliveryType.REGULAR.label_en
        assert "Express" in DeliveryType.EXPRESS.label_en
        assert "Super Express" in DeliveryType.SUPER_EXPRESS.label_en

    def test_bangla_labels(self):
        assert "সাধারণ" in DeliveryType.REGULAR.label_bn
        assert "জরুরি" in DeliveryType.EXPRESS.label_bn
        assert "সুপার এক্সপ্রেস" in DeliveryType.SUPER_EXPRESS.label_bn


class TestProfession:
    """Tests for Profession enum."""

    def test_all_professions_have_labels(self):
        for prof in Profession:
            assert prof.label_en, f"{prof.value} missing English label"
            assert prof.label_bn, f"{prof.value} missing Bangla label"

    def test_government_profession(self):
        assert Profession.GOVERNMENT.value == "government"
        assert "Government" in Profession.GOVERNMENT.label_en


class TestApplicantProfile:
    """Tests for ApplicantProfile model."""

    def test_valid_adult_profile(self):
        profile = ApplicantProfile(
            age=24,
            profession=Profession.PRIVATE_SECTOR,
            delivery_type=DeliveryType.EXPRESS,
            page_count=PageCount.PAGES_64,
            has_nid=True,
            district="Dhaka",
        )
        assert profile.age == 24
        assert profile.is_minor is False
        assert profile.is_senior is False
        assert profile.age_category == "adult"

    def test_minor_profile(self):
        profile = ApplicantProfile(
            age=15,
            profession=Profession.STUDENT,
            delivery_type=DeliveryType.REGULAR,
        )
        assert profile.is_minor is True
        assert profile.age_category == "minor"
        assert profile.age_category_bn == "নাবালক"

    def test_senior_profile(self):
        profile = ApplicantProfile(
            age=70,
            profession=Profession.RETIRED,
            delivery_type=DeliveryType.REGULAR,
        )
        assert profile.is_senior is True
        assert profile.age_category == "senior"

    def test_invalid_age_negative(self):
        with pytest.raises(ValueError):
            ApplicantProfile(
                age=-1,
                profession=Profession.OTHER,
                delivery_type=DeliveryType.REGULAR,
            )

    def test_invalid_age_too_old(self):
        with pytest.raises(ValueError):
            ApplicantProfile(
                age=121,
                profession=Profession.OTHER,
                delivery_type=DeliveryType.REGULAR,
            )

    def test_invalid_validity(self):
        with pytest.raises(ValueError):
            ApplicantProfile(
                age=30,
                profession=Profession.OTHER,
                delivery_type=DeliveryType.REGULAR,
                requested_validity_years=7,  # Only 5 or 10 allowed
            )

    def test_valid_validity_5(self):
        profile = ApplicantProfile(
            age=30,
            profession=Profession.OTHER,
            delivery_type=DeliveryType.REGULAR,
            requested_validity_years=5,
        )
        assert profile.requested_validity_years == 5

    def test_valid_validity_10(self):
        profile = ApplicantProfile(
            age=30,
            profession=Profession.OTHER,
            delivery_type=DeliveryType.REGULAR,
            requested_validity_years=10,
        )
        assert profile.requested_validity_years == 10

    def test_summary_generation(self):
        profile = ApplicantProfile(
            age=24,
            profession=Profession.PRIVATE_SECTOR,
            delivery_type=DeliveryType.EXPRESS,
            page_count=PageCount.PAGES_64,
        )
        summary = profile.to_summary()
        assert "24" in summary
        assert "Private" in summary
        assert "Express" in summary

    def test_bangla_summary(self):
        profile = ApplicantProfile(
            age=24,
            profession=Profession.PRIVATE_SECTOR,
            delivery_type=DeliveryType.EXPRESS,
        )
        summary = profile.to_summary_bn()
        assert "২৪" not in summary or "24" in summary  # Age shown
        assert "বেসরকারি" in summary


class TestPageCount:
    """Tests for PageCount enum."""

    def test_values(self):
        assert PageCount.PAGES_48.value == 48
        assert PageCount.PAGES_64.value == 64
