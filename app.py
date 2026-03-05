"""
Bangladesh E-Passport Virtual Consular Officer
Streamlit Web UI — Beautiful, production-grade interface.
"""

import streamlit as st
import logging
import time

from src.utils.logger import setup_logger
from src.utils.validators import parse_user_input
from src.models.applicant import ApplicantProfile, DeliveryType, PageCount, Profession
from src.crew.passport_crew import PassportCrew

# ── Page Config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="🇧🇩 E-Passport Virtual Consular Officer",
    page_icon="🇧🇩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ──── Global ──── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ──── Header Banner ──── */
    .hero-banner {
        background: linear-gradient(135deg, #006a4e 0%, #004d3a 40%, #003828 70%, #f42a41 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 106, 78, 0.3);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        animation: shimmer 6s ease-in-out infinite;
    }
    @keyframes shimmer {
        0%, 100% { transform: translate(-25%, -25%) rotate(0deg); }
        50% { transform: translate(-25%, -25%) rotate(180deg); }
    }
    .hero-banner h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        position: relative;
    }
    .hero-banner p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0;
        font-weight: 300;
        position: relative;
    }

    /* ──── Cards ──── */
    .info-card {
        background: linear-gradient(135deg, #f8fffe 0%, #e8f5e9 100%);
        border-left: 4px solid #006a4e;
        padding: 1.2rem 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .warning-card {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border-left: 4px solid #f57f17;
        padding: 1.2rem 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .agent-card {
        background: white;
        border: 1px solid #e0e0e0;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }

    /* ──── Status Badge ──── */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .status-eligible {
        background: #e8f5e9;
        color: #2e7d32;
    }
    .status-warning {
        background: #fff3e0;
        color: #e65100;
    }

    /* ──── Pipeline Progress ──── */
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.8rem 1rem;
        margin: 0.3rem 0;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .pipeline-step.active {
        background: #e8f5e9;
        border-left: 3px solid #006a4e;
    }
    .pipeline-step.done {
        background: #f1f8e9;
    }

    /* ──── Footer ──── */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #888;
        font-size: 0.85rem;
        border-top: 1px solid #eee;
        margin-top: 3rem;
    }

    /* ──── Sidebar Styling ──── */
    .sidebar-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    /* ──── Result Container ──── */
    .result-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def render_hero():
    """Render the hero banner."""
    st.markdown("""
    <div class="hero-banner">
        <h1>🇧🇩 Bangladesh E-Passport Virtual Consular Officer</h1>
        <p>Multi-Agent System powered by CrewAI — Your Personal Passport Advisor</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with input controls."""
    with st.sidebar:
        st.markdown("### 📝 Applicant Information")
        st.markdown("---")

        # Input mode toggle
        input_mode = st.radio(
            "Input Mode",
            ["📋 Form Input", "💬 Natural Language"],
            label_visibility="collapsed",
        )

        if input_mode == "💬 Natural Language":
            return render_natural_language_input()
        else:
            return render_form_input()


def render_natural_language_input():
    """Render natural language input."""
    st.markdown("""
    <div class="info-card">
        <strong>💡 Describe your situation</strong><br>
        Include your age, profession, urgency, and page preference.
    </div>
    """, unsafe_allow_html=True)

    user_text = st.text_area(
        "Your Description",
        placeholder=(
            "I am a 24-year-old private sector employee. "
            "I need a 64-page passport urgently because I have "
            "a business trip in two weeks. I have an NID and "
            "I live in Dhaka."
        ),
        height=180,
        label_visibility="collapsed",
    )

    submit = st.button(
        "🚀 Generate Report",
        type="primary",
        use_container_width=True,
    )

    if submit and user_text:
        try:
            profile = parse_user_input(user_text)
            return profile
        except ValueError as e:
            st.error(f"❌ {str(e)}")
            return None

    return None


def render_form_input():
    """Render structured form input."""
    # Age
    age = st.number_input("👤 Age (Years)", min_value=0, max_value=120, value=25, step=1)

    # Profession
    profession = st.selectbox(
        "💼 Profession",
        options=list(Profession),
        format_func=lambda x: x.label_en,
        index=1,  # Default to private_sector
    )

    # Delivery Type
    delivery = st.selectbox(
        "🚚 Delivery Type",
        options=list(DeliveryType),
        format_func=lambda x: x.label_en,
    )

    # Page Count
    pages = st.radio(
        "📄 Page Count",
        options=list(PageCount),
        format_func=lambda x: f"{x.value} Pages",
        horizontal=True,
    )

    st.markdown("---")
    st.markdown("### 📑 Additional Details")

    col1, col2 = st.columns(2)
    with col1:
        has_nid = st.checkbox("Has NID", value=age >= 18)
        is_renewal = st.checkbox("Renewal")
    with col2:
        has_name_change = st.checkbox("Name Change")
        has_birth_cert = st.checkbox("Birth Cert.", value=True)

    district = st.text_input("🏙️ District", value="Dhaka")

    # Validity selection (only for adults)
    requested_validity = None
    if 18 <= age <= 65:
        validity_option = st.radio(
            "📅 Requested Validity",
            ["Auto (Recommended)", "5 Years", "10 Years"],
            horizontal=True,
        )
        if validity_option == "5 Years":
            requested_validity = 5
        elif validity_option == "10 Years":
            requested_validity = 10
    elif age < 18 or age > 65:
        st.markdown("""
        <div class="warning-card">
            <strong>⚠️ Validity Restriction</strong><br>
            Applicants under 18 or over 65 can only get a <strong>5-year</strong> passport.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    submit = st.button(
        "🚀 Generate Passport Readiness Report",
        type="primary",
        use_container_width=True,
    )

    if submit:
        try:
            profile = ApplicantProfile(
                age=age,
                profession=profession,
                delivery_type=delivery,
                page_count=pages,
                has_nid=has_nid,
                has_birth_certificate=has_birth_cert,
                district=district,
                is_renewal=is_renewal,
                has_name_change=has_name_change,
                requested_validity_years=requested_validity,
            )
            return profile
        except Exception as e:
            st.error(f"❌ Invalid input: {str(e)}")
            return None

    return None


def render_agent_pipeline():
    """Render the agent pipeline visualization."""
    cols = st.columns(3)

    agents_info = [
        ("🛡️", "Policy Guardian", "Eligibility & validity assessment"),
        ("💰", "Fee Calculator", "Exact BDT fee with 15% VAT"),
        ("📋", "Document Architect", "Customized checklist & final report"),
    ]

    for col, (icon, name, desc) in zip(cols, agents_info):
        with col:
            st.markdown(f"""
            <div class="agent-card">
                <div style="font-size: 2rem; text-align: center;">{icon}</div>
                <div style="text-align: center; font-weight: 600; margin: 0.5rem 0;">{name}</div>
                <div style="text-align: center; color: #666; font-size: 0.85rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def render_profile_summary(profile: ApplicantProfile):
    """Render the applicant profile summary."""
    st.markdown("### 📋 Applicant Profile Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👤 Age", f"{profile.age} yrs")
    with col2:
        st.metric("💼 Profession", profile.profession.label_en.split()[0])
    with col3:
        st.metric("🚚 Delivery", profile.delivery_type.value.replace("_", " ").title())
    with col4:
        st.metric("📄 Pages", str(profile.page_count.value))


def run_pipeline(profile: ApplicantProfile):
    """Run the agent pipeline and display results."""
    render_profile_summary(profile)

    st.markdown("---")
    st.markdown("### ⚡ Running Multi-Agent Pipeline")

    # Progress indicators
    progress_bar = st.progress(0, text="Initializing agents...")

    status_container = st.empty()

    try:
        # Initialize crew
        status_container.info("🔄 Initializing Virtual Consular Officer crew...")
        progress_bar.progress(10, text="Creating agents...")

        crew = PassportCrew(verbose=False)

        progress_bar.progress(25, text="🛡️ Policy Guardian analyzing eligibility...")
        status_container.info("🛡️ **Policy Guardian** is analyzing eligibility rules...")

        # Small delay for UX
        time.sleep(0.5)
        progress_bar.progress(40, text="💰 Fee Calculator computing costs...")
        status_container.info("💰 **Fee Calculator** is computing exact fees...")

        time.sleep(0.5)
        progress_bar.progress(60, text="📋 Document Architect preparing checklist...")
        status_container.info("📋 **Document Architect** is generating your checklist...")

        # Run the actual pipeline
        result = crew.run(profile)

        progress_bar.progress(100, text="✅ Report complete!")
        status_container.success("✅ **Passport Readiness Report generated successfully!**")

        # Display the result
        st.markdown("---")
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=result,
            file_name="passport_readiness_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    except Exception as e:
        progress_bar.progress(100, text="⚠️ Falling back to local database...")
        status_container.warning(f"⚠️ Agent pipeline encountered an issue. Using fallback report.")

        # Generate fallback report
        fallback_crew = PassportCrew.__new__(PassportCrew)
        result = fallback_crew._generate_fallback_report(profile, str(e))

        st.markdown("---")
        st.markdown(result)

        st.download_button(
            label="📥 Download Report (Markdown)",
            data=result,
            file_name="passport_readiness_report_fallback.md",
            mime="text/markdown",
            use_container_width=True,
        )


def main():
    """Main Streamlit application."""
    # Setup logging
    setup_logger(level=logging.INFO)

    # Hero banner
    render_hero()

    # Agent pipeline visualization
    render_agent_pipeline()

    st.markdown("---")

    # Sidebar input
    profile = render_sidebar()

    # Main content area
    if profile:
        run_pipeline(profile)
    else:
        # Landing state
        st.markdown("""
        <div class="info-card">
            <strong>👈 Fill in the applicant details in the sidebar</strong> to generate
            your personalized Passport Readiness Report.<br><br>
            Our AI-powered multi-agent system will analyze:
            <ul>
                <li>🛡️ <strong>Eligibility</strong> — Age-based validity & ID requirements</li>
                <li>💰 <strong>Fees</strong> — Exact BDT cost with 15% VAT breakdown</li>
                <li>📋 <strong>Documents</strong> — Profession-specific checklist</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Show example scenario
        with st.expander("📌 Example Scenario"):
            st.markdown("""
            > *"I am a 24-year-old private sector employee. I need a 64-page passport
            > urgently because I have a business trip in two weeks. I have an NID
            > and I live in Dhaka."*

            **Expected Output:**
            | Field | Value |
            |-------|-------|
            | Validity | 10 Years |
            | Delivery Type | Express |
            | Total Fee | 9,919 BDT |
            | Key Documents | NID, Employment Certificate, Application Form |
            """)

        # Show fee table
        with st.expander("📊 2026 Fee Structure Reference"):
            from src.database.fee_structure import FeeDatabase
            st.markdown(FeeDatabase.get_fee_table())

    # Footer
    st.markdown("""
    <div class="footer">
        🇧🇩 Bangladesh E-Passport Virtual Consular Officer • Multi-Agent System powered by CrewAI<br>
        Built with ❤️ by Amar • Data based on 2026 Official Fee Structure
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
