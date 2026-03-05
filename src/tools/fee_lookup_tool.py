"""
Fee Lookup Tool for CrewAI Agents
Wraps the local FeeDatabase for use by the Fee Calculator agent.
Includes fallback handling for reliable operation.
"""

import json
import logging
from crewai.tools import tool
from src.database.fee_structure import FeeDatabase

logger = logging.getLogger(__name__)


@tool("Fee Lookup Tool")
def fee_lookup(page_count: int, delivery_type: str) -> str:
    """
    Look up Bangladesh E-Passport fees based on page count and delivery type.
    Returns a detailed fee breakdown including base fee, VAT amount, and total amount in BDT.

    Args:
        page_count: Number of passport pages. Must be 48 or 64.
        delivery_type: Delivery speed. Must be one of: 'regular', 'express', or 'super_express'.

    Returns:
        JSON string with fee breakdown details.
    """
    try:
        logger.info(f"Looking up fee: pages={page_count}, delivery={delivery_type}")

        # Normalize delivery type
        delivery_type = delivery_type.lower().strip().replace(" ", "_")

        result = FeeDatabase.get_fee(page_count, delivery_type)

        if result is None:
            error_msg = (
                f"Invalid parameters: page_count={page_count}, delivery_type={delivery_type}. "
                f"Valid page counts: 48, 64. "
                f"Valid delivery types: regular, express, super_express."
            )
            logger.warning(error_msg)
            return json.dumps({
                "error": True,
                "message": error_msg,
            }, indent=2)

        logger.info(f"Fee found: {result['total_fee']} BDT")
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error in fee lookup: {e}")
        return json.dumps({
            "error": True,
            "message": f"Error looking up fee: {str(e)}. Please try again.",
            "fallback": True,
            "note": "Unable to determine exact fee. Please consult the official fee schedule.",
            "source": "Fallback — Error Recovery",
        }, indent=2, ensure_ascii=False)


@tool("Full Fee Table Tool")
def get_full_fee_table() -> str:
    """
    Get the complete Bangladesh E-Passport fee schedule in Markdown table format.
    Use this when you need to show all available fee options.

    Returns:
        Markdown-formatted table of all passport fees.
    """
    try:
        logger.info("Generating full fee table")
        return FeeDatabase.get_fee_table()
    except Exception as e:
        logger.error(f"Error generating fee table: {e}")
        return "Error generating fee table. Please consult the official fee schedule."
