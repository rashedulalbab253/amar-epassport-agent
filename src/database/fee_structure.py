"""
Bangladesh E-Passport Fee Structure Database (2026)
Local fallback data source for fee calculations.
Source: Department of Immigration & Passports, Bangladesh.

All fees are in BDT (Bangladeshi Taka).
VAT rate: 15% on base fee.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class FeeEntry:
    """Represents a single fee entry."""
    base_fee: float
    vat_rate: float = 0.15
    description_en: str = ""
    description_bn: str = ""

    @property
    def vat_amount(self) -> float:
        return round(self.base_fee * self.vat_rate, 2)

    @property
    def total_fee(self) -> float:
        return round(self.base_fee + self.vat_amount, 2)


class FeeDatabase:
    """
    Local database containing the 2026 official Bangladesh E-Passport fee structure.
    Acts as a fallback when external data sources are unavailable.
    """

    VAT_RATE = 0.15

    # ─────────────────────────────────────────────────────────────
    # 2026 Official Fee Structure (Base fees before VAT)
    # ─────────────────────────────────────────────────────────────
    NEW_PASSPORT_FEES: Dict[str, Dict[str, FeeEntry]] = {
        "48": {
            "regular": FeeEntry(
                base_fee=3450.00,
                description_en="48-page passport, Regular delivery (21 working days)",
                description_bn="৪৮ পৃষ্ঠার পাসপোর্ট, সাধারণ ডেলিভারি (২১ কার্যদিবস)",
            ),
            "express": FeeEntry(
                base_fee=6900.00,
                description_en="48-page passport, Express delivery (7 working days)",
                description_bn="৪৮ পৃষ্ঠার পাসপোর্ট, জরুরি ডেলিভারি (৭ কার্যদিবস)",
            ),
            "super_express": FeeEntry(
                base_fee=8625.00,
                description_en="48-page passport, Super Express delivery (2-3 working days)",
                description_bn="৪৮ পৃষ্ঠার পাসপোর্ট, সুপার এক্সপ্রেস ডেলিভারি (২-৩ কার্যদিবস)",
            ),
        },
        "64": {
            "regular": FeeEntry(
                base_fee=5750.00,
                description_en="64-page passport, Regular delivery (21 working days)",
                description_bn="৬৪ পৃষ্ঠার পাসপোর্ট, সাধারণ ডেলিভারি (২১ কার্যদিবস)",
            ),
            "express": FeeEntry(
                base_fee=8625.00,
                description_en="64-page passport, Express delivery (7 working days)",
                description_bn="৬৪ পৃষ্ঠার পাসপোর্ট, জরুরি ডেলিভারি (৭ কার্যদিবস)",
            ),
            "super_express": FeeEntry(
                base_fee=11500.00,
                description_en="64-page passport, Super Express delivery (2-3 working days)",
                description_bn="৬৪ পৃষ্ঠার পাসপোর্ট, সুপার এক্সপ্রেস ডেলিভারি (২-৩ কার্যদিবস)",
            ),
        },
    }

    # Additional service fees
    ADDITIONAL_FEES: Dict[str, FeeEntry] = {
        "lost_passport_penalty": FeeEntry(
            base_fee=15000.00,
            description_en="Lost passport penalty fee",
            description_bn="পাসপোর্ট হারানোর জরিমানা",
        ),
        "damaged_passport_penalty": FeeEntry(
            base_fee=15000.00,
            description_en="Damaged passport penalty fee",
            description_bn="পাসপোর্ট নষ্ট হওয়ার জরিমানা",
        ),
        "correction_fee": FeeEntry(
            base_fee=3450.00,
            description_en="Passport information correction fee",
            description_bn="পাসপোর্ট তথ্য সংশোধন ফি",
        ),
    }

    @classmethod
    def get_fee(
        cls,
        page_count: int,
        delivery_type: str,
        is_renewal: bool = False,
    ) -> Optional[Dict]:
        """
        Look up the passport fee based on page count and delivery type.

        Args:
            page_count: Number of pages (48 or 64)
            delivery_type: Delivery speed ('regular', 'express', 'super_express')
            is_renewal: Whether this is a renewal

        Returns:
            Dictionary with fee breakdown or None if invalid parameters.
        """
        page_key = str(page_count)
        delivery_key = delivery_type.lower().strip()

        if page_key not in cls.NEW_PASSPORT_FEES:
            return None

        if delivery_key not in cls.NEW_PASSPORT_FEES[page_key]:
            return None

        fee_entry = cls.NEW_PASSPORT_FEES[page_key][delivery_key]

        return {
            "page_count": page_count,
            "delivery_type": delivery_type,
            "base_fee": fee_entry.base_fee,
            "vat_rate": f"{fee_entry.vat_rate * 100:.0f}%",
            "vat_amount": fee_entry.vat_amount,
            "total_fee": fee_entry.total_fee,
            "description_en": fee_entry.description_en,
            "description_bn": fee_entry.description_bn,
            "currency": "BDT",
            "is_renewal": is_renewal,
            "source": "Local Database — 2026 Official Fee Structure",
        }

    @classmethod
    def get_fee_table(cls) -> str:
        """Generate a complete fee table in Markdown format."""
        lines = [
            "## Bangladesh E-Passport Fee Structure (2026)",
            "",
            "| Pages | Delivery Type | Base Fee (BDT) | VAT (15%) | Total (BDT) |",
            "|-------|--------------|----------------|-----------|-------------|",
        ]
        for page_key, deliveries in cls.NEW_PASSPORT_FEES.items():
            for delivery_key, entry in deliveries.items():
                delivery_label = delivery_key.replace("_", " ").title()
                lines.append(
                    f"| {page_key} | {delivery_label} | "
                    f"{entry.base_fee:,.0f} | {entry.vat_amount:,.0f} | "
                    f"**{entry.total_fee:,.0f}** |"
                )
        lines.append("")
        lines.append("*All fees include 15% VAT as per government regulation.*")
        return "\n".join(lines)

    @classmethod
    def get_additional_fee(cls, fee_type: str) -> Optional[Dict]:
        """Look up additional service fees."""
        if fee_type not in cls.ADDITIONAL_FEES:
            return None
        entry = cls.ADDITIONAL_FEES[fee_type]
        return {
            "fee_type": fee_type,
            "base_fee": entry.base_fee,
            "vat_amount": entry.vat_amount,
            "total_fee": entry.total_fee,
            "description_en": entry.description_en,
            "description_bn": entry.description_bn,
        }
