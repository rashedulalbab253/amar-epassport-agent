# 🇧🇩 Bangladesh E-Passport Virtual Consular Officer

> **Multi-Agent System (MAS) powered by CrewAI** — Your personal passport application advisor

A production-level multi-agent system that acts as a "Virtual Consular Officer" for the Bangladesh E-Passport Portal. Given an applicant's profile (age, profession, urgency), it generates a comprehensive **Passport Readiness Report** in both English and Bangla.

---

## 🏗️ Architecture

```
User Input ──→ Input Parser ──→ Passport Crew Orchestrator
                                        │
                    ┌───────────────────┤
                    ▼                   ▼                   ▼
            🛡️ Policy Guardian   💰 Fee Calculator   📋 Document Architect
            (Eligibility)        (Fee + VAT)         (Checklist + Report)
                    │                   │                   │
                    ▼                   ▼                   ▼
            Policy Lookup Tool   Fee Lookup Tool     Document Lookup Tool
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        ▼
                              📊 Local Database (Fallback)
                                        │
                                        ▼
                        📄 Passport Readiness Report
                            (English + বাংলা)
```

### The Three Agents

| Agent | Role | Responsibility |
|-------|------|---------------|
| 🛡️ **Policy Guardian** | Bangladesh Passport Policy Expert | Determines validity (5/10 years), required ID (NID/BRC), flags inconsistencies |
| 💰 **Fee Calculator** | Financial Auditor | Calculates exact BDT fee with 15% VAT using 2026 fee structure |
| 📋 **Document Architect** | Documentation Officer | Generates customized checklist, compiles final report |

### Task Delegation Chain

```
Task 1 (Policy Guardian) ──context──→ Task 2 (Fee Calculator)
         │                                      │
         └────────────── context ───────────────→ Task 3 (Document Architect)
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone <repo-url>
cd amar-epassport-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example env file
copy .env.example .env     # Windows
# cp .env.example .env     # Linux/Mac

# Edit .env and add your API key
# For Google Gemini:
#   GOOGLE_API_KEY=your_key_here
#   LLM_PROVIDER=google
#
# For OpenAI:
#   OPENAI_API_KEY=your_key_here
#   LLM_PROVIDER=openai
```

### 3. Run the Application

#### Web UI (Streamlit)
```bash
streamlit run app.py
```

#### CLI — Interactive Mode
```bash
python main.py
```

#### CLI — Natural Language
```bash
python main.py --text "I am a 24-year-old private sector employee. I need a 64-page passport urgently because I have a business trip in two weeks. I have an NID and I live in Dhaka."
```

#### CLI — Structured Arguments
```bash
python main.py --age 24 --profession private_sector --delivery express --pages 64 --nid --district Dhaka
```

---

## 📝 Example

### Input
```
"I am a 24-year-old private sector employee. I need a 64-page passport urgently 
because I have a business trip in two weeks. I have an NID and I live in Dhaka."
```

### Output (Summary Table)

| Field | Value |
|-------|-------|
| **Age Category** | Adult (18-65) |
| **Validity** | 10 Years |
| **Delivery Type** | Express (7 working days) |
| **Base Fee** | 8,625 BDT |
| **VAT (15%)** | 1,294 BDT |
| **Total Fee** | 9,919 BDT |
| **Required ID** | National ID Card (NID) |
| **Documents** | NID, Employment Certificate, Application Form, Photographs, Birth Certificate, Bank Receipt |

---

## ⚠️ Error Handling

### Inconsistency Flagging
If a 15-year-old requests a 10-year passport:
```
⚠️ POLICY VIOLATION: A 10-year passport is NOT permitted for a 15-year-old (minor).
Allowed validity: 5 year(s) only.
The application will be automatically adjusted to 5-year validity.
```

### Fallback Mechanism
If the LLM agent pipeline fails (API errors, network issues), the system automatically falls back to the **local database** containing:
- Policy rules for all age categories
- 2026 official fee structure
- Document requirements for all professions

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_database.py -v
```

---

## 📁 Project Structure

```
amar-epassport-agent/
├── main.py                          # CLI entry point
├── app.py                           # Streamlit web UI
├── requirements.txt                 # Dependencies
├── .env.example                     # Environment template
├── .gitignore
├── README.md
├── config/
│   ├── agents.yaml                  # Agent persona config
│   └── tasks.yaml                   # Task config
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── policy_guardian.py       # 🛡️ Eligibility agent
│   │   ├── fee_calculator.py        # 💰 Fee agent
│   │   └── document_architect.py    # 📋 Document agent
│   ├── tasks/
│   │   ├── eligibility_task.py      # Policy assessment task
│   │   ├── fee_task.py              # Fee calculation task
│   │   └── checklist_task.py        # Checklist + report task
│   ├── crew/
│   │   └── passport_crew.py         # Crew orchestrator
│   ├── models/
│   │   └── applicant.py             # Pydantic data models
│   ├── database/
│   │   ├── fee_structure.py         # Local fee data
│   │   ├── policy_rules.py          # Local policy data
│   │   └── document_requirements.py # Local document data
│   ├── tools/
│   │   ├── fee_lookup_tool.py       # CrewAI fee tool
│   │   ├── policy_lookup_tool.py    # CrewAI policy tool
│   │   └── document_lookup_tool.py  # CrewAI document tool
│   └── utils/
│       ├── logger.py                # Centralized logging
│       └── validators.py            # Input parsing & validation
└── tests/
    ├── test_models.py               # Model tests
    ├── test_database.py             # Database tests
    └── test_validators.py           # Parser tests
```

---

## 📊 2026 Fee Structure

| Pages | Delivery | Base Fee | VAT (15%) | Total |
|-------|----------|----------|-----------|-------|
| 48 | Regular (21 days) | 3,450 ৳ | 518 ৳ | **3,968 ৳** |
| 48 | Express (7 days) | 6,900 ৳ | 1,035 ৳ | **7,935 ৳** |
| 48 | Super Express (2-3 days) | 8,625 ৳ | 1,294 ৳ | **9,919 ৳** |
| 64 | Regular (21 days) | 5,750 ৳ | 863 ৳ | **6,613 ৳** |
| 64 | Express (7 days) | 8,625 ৳ | 1,294 ৳ | **9,919 ৳** |
| 64 | Super Express (2-3 days) | 11,500 ৳ | 1,725 ৳ | **13,225 ৳** |

---

## 🛡️ Technology Stack

- **Framework**: CrewAI (Multi-Agent Orchestration)
- **LLM**: Google Gemini / OpenAI GPT-4o  
- **Web UI**: Streamlit
- **Data Models**: Pydantic v2
- **Logging**: Rich + File-based
- **Testing**: Pytest
- **Language**: Python 3.10+

---

## 📄 License

MIT License — Built by Rashedul Albab.
