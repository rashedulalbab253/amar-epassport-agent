"""
Bangladesh E-Passport Virtual Consular Officer
CLI Entry Point — Run the multi-agent system from the command line.
"""

import sys
import argparse
import logging

from src.utils.logger import setup_logger
from src.utils.validators import parse_user_input
from src.models.applicant import ApplicantProfile, DeliveryType, PageCount, Profession
from src.crew.passport_crew import PassportCrew


def run_interactive():
    """Run in interactive mode — prompt user for input."""
    print("\n" + "=" * 65)
    print("  🇧🇩  Bangladesh E-Passport Virtual Consular Officer")
    print("  Multi-Agent System powered by CrewAI")
    print("=" * 65 + "\n")

    print("You can describe your situation in natural language, or use the")
    print("structured input mode. Type 'q' to quit.\n")

    mode = input("Choose mode [1] Natural Language  [2] Structured Input: ").strip()

    if mode == "1":
        print("\nDescribe your passport application requirements:")
        print("(Example: 'I am a 24-year-old private sector employee. I need a")
        print(" 64-page passport urgently because I have a business trip in two")
        print(" weeks. I have an NID and I live in Dhaka.')\n")

        user_input = input("Your description: ").strip()
        if not user_input or user_input.lower() == "q":
            print("Goodbye!")
            return

        try:
            profile = parse_user_input(user_input)
        except ValueError as e:
            print(f"\n❌ Error parsing input: {e}")
            print("Please try again with more details.")
            return

    elif mode == "2":
        profile = get_structured_input()
        if profile is None:
            return
    else:
        print("Invalid selection. Please choose 1 or 2.")
        return

    print("\n📋 Parsed Applicant Profile:")
    print("-" * 40)
    print(profile.to_summary())
    print("-" * 40)

    confirm = input("\nProceed with this profile? [Y/n]: ").strip().lower()
    if confirm == "n":
        print("Cancelled.")
        return

    # Run the crew
    print("\n🚀 Starting Multi-Agent Assessment Pipeline...\n")
    crew = PassportCrew(verbose=True)
    result = crew.run(profile)

    print("\n" + "=" * 65)
    print("📄 PASSPORT READINESS REPORT")
    print("=" * 65 + "\n")
    print(result)


def get_structured_input():
    """Get structured input from the user."""
    try:
        print("\n--- Structured Input Mode ---\n")

        age = int(input("Age (years): ").strip())

        print("\nProfession options:")
        for i, p in enumerate(Profession, 1):
            print(f"  {i:2d}. {p.label_en}")
        prof_idx = int(input("Select profession number: ").strip()) - 1
        profession = list(Profession)[prof_idx]

        print("\nDelivery type options:")
        for i, d in enumerate(DeliveryType, 1):
            print(f"  {i}. {d.label_en}")
        del_idx = int(input("Select delivery type number: ").strip()) - 1
        delivery = list(DeliveryType)[del_idx]

        print("\nPage count options:")
        print("  1. 48 pages")
        print("  2. 64 pages")
        page_idx = int(input("Select page count: ").strip())
        page_count = PageCount.PAGES_48 if page_idx == 1 else PageCount.PAGES_64

        has_nid = input("Do you have a National ID (NID)? [y/N]: ").strip().lower() == "y"
        district = input("District (default: Dhaka): ").strip() or "Dhaka"
        is_renewal = input("Is this a renewal? [y/N]: ").strip().lower() == "y"
        has_name_change = input("Do you have a name change? [y/N]: ").strip().lower() == "y"

        validity = None
        if 18 <= age <= 65:
            val_input = input("Requested validity (5 or 10 years, press Enter for auto): ").strip()
            if val_input:
                validity = int(val_input)

        return ApplicantProfile(
            age=age,
            profession=profession,
            delivery_type=delivery,
            page_count=page_count,
            has_nid=has_nid,
            has_birth_certificate=True,
            district=district,
            is_renewal=is_renewal,
            has_name_change=has_name_change,
            requested_validity_years=validity,
        )

    except (ValueError, IndexError) as e:
        print(f"\n❌ Invalid input: {e}")
        return None
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return None


def run_with_args(args):
    """Run with command-line arguments."""
    if args.text:
        # Natural language mode
        profile = parse_user_input(args.text)
    else:
        # Structured mode from args
        profile = ApplicantProfile(
            age=args.age,
            profession=Profession(args.profession),
            delivery_type=DeliveryType(args.delivery),
            page_count=PageCount(args.pages),
            has_nid=args.nid,
            has_birth_certificate=True,
            district=args.district,
            is_renewal=args.renewal,
            has_name_change=args.name_change,
            requested_validity_years=args.validity,
        )

    crew = PassportCrew(verbose=not args.quiet)
    result = crew.run(profile)
    print(result)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🇧🇩 Bangladesh E-Passport Virtual Consular Officer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py

  # Natural language mode
  python main.py --text "I am a 24-year-old private sector employee..."

  # Structured arguments
  python main.py --age 24 --profession private_sector --delivery express --pages 64

  # Test with a minor (should flag 10-year request)
  python main.py --age 15 --profession student --delivery regular --validity 10
        """,
    )

    parser.add_argument("--text", "-t", type=str, help="Natural language description")
    parser.add_argument("--age", "-a", type=int, help="Applicant age")
    parser.add_argument(
        "--profession", "-p", type=str,
        choices=[p.value for p in Profession],
        help="Profession category",
    )
    parser.add_argument(
        "--delivery", "-d", type=str,
        choices=[d.value for d in DeliveryType],
        default="regular",
        help="Delivery type",
    )
    parser.add_argument("--pages", type=int, choices=[48, 64], default=48, help="Page count")
    parser.add_argument("--nid", action="store_true", help="Has National ID")
    parser.add_argument("--district", type=str, default="Dhaka", help="District")
    parser.add_argument("--renewal", action="store_true", help="Is renewal")
    parser.add_argument("--name-change", action="store_true", help="Has name change")
    parser.add_argument("--validity", type=int, choices=[5, 10], help="Requested validity years")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress verbose output")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.WARNING if args.quiet else logging.INFO
    setup_logger(level=log_level)

    if args.text or args.age:
        run_with_args(args)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
