# PRD — AI-Driven Invoice Intake, Validation and Review Pipeline

## 1. Project Title
AI-Driven Invoice Intake, Validation and Review Pipeline in Power Automate

---

## 2. Background
Many organizations receive invoices through email or document drop folders in multiple formats and quality levels. Manual invoice handling is slow, error-prone, and difficult to scale. This project aims to simulate a realistic consulting-style automation case where incoming invoices are ingested, analyzed using AI, validated with business rules, and routed either to automatic acceptance or human review.

This project is designed as an interview portfolio case for a role focused on AI, automation, process improvement, and business value realization.

---

## 3. Problem Statement
Finance and operations teams often spend too much time on repetitive invoice handling:
- Opening attachments manually
- Reading invoice metadata manually
- Registering vendor, amounts, dates, and invoice IDs manually
- Detecting duplicate or suspicious invoices too late
- Escalating incomplete or low-quality invoices manually

The business needs a solution that:
- Reduces repetitive manual work
- Improves intake speed
- Improves data quality
- Identifies suspicious or incomplete invoices
- Preserves human review for uncertain cases

---

## 4. Goal
Build a realistic invoice automation pipeline using Power Automate and AI services that can:
1. Receive invoices from a folder
2. Extract structured invoice data
3. Apply validation and business rules
4. Route invoices into:
   - Approved
   - Needs review
   - Suspected duplicate/fraud
5. Log all outcomes
6. Produce a daily summary
7. Support a simple human review process

---

## 5. Success Criteria
The solution is considered successful if it can:
- Process at least 30 synthetic invoices
- Correctly ingest files from a monitored location
- Extract core fields from clean invoices
- Detect low-quality or incomplete invoices and send them to review
- Detect duplicates using invoice ID, vendor and amount logic
- Log decisions consistently in a structured format
- Generate a daily summary of processing outcomes
- Demonstrate clear business value in an interview setting

---

## 6. Scope

### In Scope
- Synthetic invoice dataset generation
- Different invoice types and layouts
- Clean, noisy, duplicate and suspicious invoice scenarios
- Power Automate ingestion flow
- AI-based invoice field extraction
- Business rule validation
- Logging to SharePoint list or Excel table
- Human review queue
- Daily summary flow
- Architecture documentation
- Test matrix and test execution
- Interview-ready narrative

### Out of Scope
- Real ERP integration
- Real financial posting
- Real vendor payment execution
- Production-grade security model
- Production-grade fraud detection
- Advanced front-end UX
- Complex Power Apps solution unless time remains

---

## 7. Primary User Personas

### Persona 1 — AP/Finance Clerk
Needs incoming invoices processed faster with fewer manual steps.

### Persona 2 — Reviewer/Controller
Needs suspicious or incomplete invoices flagged with clear reasons.

### Persona 3 — Automation Consultant
Needs a solution that is explainable, testable, and clearly tied to business value.

---

## 8. User Stories

### Intake
As a finance clerk, I want invoices dropped into a folder to be processed automatically so that I do not need to manually inspect every file.

### Extraction
As a finance clerk, I want invoice number, vendor name, dates, and total amount extracted automatically so that manual registration is reduced.

### Validation
As a reviewer, I want invoices with missing fields, low confidence, duplicates, or suspicious values routed to review so that risky data is not auto-approved.

### Logging
As a consultant, I want every processed invoice logged with status and reason so that I can demonstrate traceability and governance.

### Review
As a reviewer, I want a simple review queue so that I can approve or reject uncertain invoices.

### Reporting
As a manager, I want a daily summary of processed invoices so that I can understand automation performance.

---

## 9. Functional Requirements

### FR1 — File Intake
The solution shall monitor a designated folder for new invoice files.

### FR2 — Supported File Types
The solution should support PDF and image-based invoice inputs for testing.

### FR3 — AI Extraction
The solution shall attempt to extract:
- Vendor name
- Invoice ID
- Invoice date
- Due date
- Currency
- Tax amount
- Total amount

### FR4 — Mandatory Field Validation
The solution shall route invoices to review if critical fields are missing.

### FR5 — Confidence Validation
The solution shall route invoices to review when extraction confidence is below a chosen threshold.

### FR6 — Duplicate Detection
The solution shall detect likely duplicates based on:
- Vendor name
- Invoice ID
- Total amount

### FR7 — Suspicious Pattern Detection
The solution shall flag suspicious invoices when:
- Due date is earlier than invoice date
- Amount is unusually high
- Vendor is not on whitelist
- Fields appear inconsistent

### FR8 — Logging
The solution shall store processed invoice data and status in a structured log.

### FR9 — Review Queue
The solution shall write review-required invoices to a separate review queue or mark them clearly in the log.

### FR10 — Daily Summary
The solution shall produce a daily summary with counts per outcome category.

---

## 10. Non-Functional Requirements

### NFR1 — Explainability
The flow must be easy to explain in an interview.

### NFR2 — Traceability
Every decision should have a reason attached.

### NFR3 — Testability
The project must include test data, expected outcomes, and a test matrix.

### NFR4 — Modularity
The solution should be structured into clear flows and reusable data assets.

### NFR5 — Realism
The use case should feel realistic enough for a consulting/automation discussion.

---

## 11. Input Dataset Design

### Categories
1. Clean invoices
2. Noisy but legitimate invoices
3. Missing-field invoices
4. Duplicate invoices
5. Suspicious/fake invoices

### Target Volume
At least 30 invoices total.

### Example Distribution
- 10 clean
- 8 noisy
- 6 missing fields
- 3 duplicates
- 5 suspicious/fake

---

## 12. Ground Truth / Expected Output
Each invoice must have a corresponding expected output row including:
- File name
- Expected vendor
- Expected invoice ID
- Expected invoice date
- Expected due date
- Expected currency
- Expected total
- Category
- Expected outcome
- Notes

Expected outcomes:
- Approved
- Needs review
- Suspected duplicate
- Suspected fraud

---

## 13. Proposed System Components

### Component A — Synthetic Data Generator
Python scripts in Cursor that generate invoice documents and expected-output metadata.

### Component B — Storage Layer
OneDrive or SharePoint folder for incoming invoice files.

### Component C — Extraction Layer
Power Automate flow with AI extraction action.

### Component D — Rule Engine
Conditions in Power Automate for:
- Missing fields
- Low confidence
- Duplicates
- Suspicious dates
- Vendor whitelist checks
- High amount checks

### Component E — Logging Layer
SharePoint list or Excel table with structured processing results.

### Component F — Review Layer
Simple queue/list where uncertain invoices can be reviewed.

### Component G — Reporting Layer
Daily summary flow via email or Teams.

---

## 14. Status Definitions

### Approved
Invoice passed extraction and validation checks.

### Needs review
Invoice could not be trusted automatically and requires human review.

### Suspected duplicate
Invoice appears to match an earlier invoice based on duplicate logic.

### Suspected fraud
Invoice has suspicious patterns and should be reviewed with high priority.

---

## 15. Business Rules

### Rule Group A — Missing Fields
If vendor name, invoice ID, invoice date, or total amount is missing:
- Status = Needs review

### Rule Group B — Low Confidence
If confidence is below threshold:
- Status = Needs review

### Rule Group C — Duplicate Detection
If same vendor + same invoice ID + same amount already exists:
- Status = Suspected duplicate

### Rule Group D — Vendor Whitelist
If vendor is not in approved vendor list:
- Status = Needs review or Suspected fraud depending on context

### Rule Group E — Date Logic
If due date is earlier than invoice date:
- Status = Suspected fraud

### Rule Group F — Amount Logic
If amount exceeds anomaly threshold:
- Status = Needs review

---

## 16. Risks and Assumptions

### Risks
- AI extraction may require credits or limited access
- Invoice formats may vary too much
- Time is limited
- Login/environment issues in Power Platform

### Assumptions
- A Power Automate environment is available
- AI extraction is accessible or can be simulated
- Synthetic data is sufficient for demo purposes
- SharePoint or Excel logging is available

---

## 17. Fallback Strategy
If AI extraction is not available:
- Simulate extraction via pre-generated metadata
- Continue with routing, validation, logging and review logic
- Be transparent in interview about what was simulated

---

## 18. Deliverables
1. Synthetic invoice dataset
2. Ground truth CSV
3. Power Automate Flow 1: Intake + Extraction + Logging
4. Power Automate Flow 2: Validation + Routing
5. Power Automate Flow 3: Daily Summary
6. Optional human review flow
7. Architecture document
8. Test matrix
9. Test results
10. Interview pitch

---

## 19. Definition of Done
The project is done when:
- A monitored folder receives invoices
- At least 30 invoices are available
- Extraction is working or credibly simulated
- Business rules route invoices into correct categories
- Results are logged
- Daily summary works
- Test cases are executed
- Documentation is complete
- A concise interview story is ready

---

## 20. Interview Positioning
This project should be presented not as “a cool demo,” but as:
- A business automation use case
- A realistic AP/finance workflow
- An example of combining AI + automation + governance + human review
- A case designed with scalability and operational reasoning in mind
