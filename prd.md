# PRD — AI-Driven Invoice Intake, Validation and Review Pipeline

## Document status (read first)

**Original intent:** The case was first scoped around **Microsoft Power Platform**—**Power Automate** for orchestration, **SharePoint or OneDrive** for intake/storage, **AI Builder** and/or **Azure AI Document Intelligence** (Form Recognizer) for extraction, and structured logging in SharePoint or Excel (plus optional daily summary via email/Teams).

**Why that integration was not completed:** The available environment lacked a fully provisioned Microsoft 365 / Azure backend: limited tenant rights, **no active SharePoint site** for standard connectors, **OneDrive** not usable as a reliable trigger, **no AI Builder premium entitlement**, and **no Azure subscription** (therefore no Document Intelligence keys or endpoint). **The blocker was licensing, provisioning, and permissions—not the validity of the business design.**

**What this repository actually delivers:** A **Python reference implementation** (`docs/src/process_invoice.py`, `docs/src/batch_eval.py`, `README.md`) that implements the **same logical pipeline**: read invoice PDFs from a folder (batch), extract text (`pdfplumber`), structured field extraction via **OpenAI**, normalization and validation, **rule-based duplicate detection** (same invoice ID, or same vendor + invoice date + total amount within tolerance vs. prior items in the batch), routing to `Approved` or `Needs review`, and **measurable evaluation** against ground-truth CSVs. **This is not a deployed Power Automate solution.** It is an end-to-end, testable substitute for interviews and demos.

**Interview framing:** Lead with the **business problem and system** (ingest → extract → validate → route → measure). State clearly that **Power Automate was the planned integration layer** but could not be finished E2E in the given tenant; the Python pipeline **proves the rules, AI-assisted extraction, and quality metrics** that would sit behind similar connectors in production.

---

## 1. Project Title
AI-Driven Invoice Intake, Validation and Review Pipeline *(PRD product intent; **reference build = Python in this repo**, not a completed Power Automate integration)*

---

## 2. Background
Many organizations receive invoices through email or document drop folders in multiple formats and quality levels. Manual invoice handling is slow, error-prone, and difficult to scale. This project aims to simulate a realistic consulting-style automation case where incoming invoices are ingested, analyzed using AI, validated with business rules, and routed either to automatic acceptance or human review.

This project is designed as an interview portfolio case for a role focused on AI, automation, process improvement, and business value realization.

**Implementation note:** The first design target was **Power Automate** with **SharePoint/OneDrive**, **AI Builder**, and/or **Azure AI Document Intelligence**. End-to-end delivery on Power Platform was **not achievable** in the available tenant for the reasons summarized in **Document status** above. The **delivered software** is the Python pipeline in this repository, aligned with the same acceptance themes (traceability, rules, human review for uncertainty, testability).

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
Deliver a realistic invoice automation pipeline that can:
1. Receive invoices from a folder *(batch directory in the Python build; monitored folder was the Power Automate target)*
2. Extract structured invoice data *(OpenAI in repo; AI Builder / Document Intelligence in the original platform plan)*
3. Apply validation and business rules
4. Route invoices into:
   - Approved
   - Needs review
   - *(PRD also describes suspected duplicate/fraud statuses; the reference code focuses on `Approved` / `Needs review` with duplicate explained via fields—extend as needed)*
5. Log all outcomes *(CSV outputs + console in Python; SharePoint/Excel in the original plan)*
6. Produce a daily summary *(not implemented in the Python MVP—was intended as a separate Power Automate flow)*
7. Support a simple human review process *(represented by `Needs review` and reason strings; no separate queue UI in repo)*

---

## 5. Success Criteria
The solution is considered successful if it can:
- Process at least 30 synthetic invoices
- Correctly ingest files from a monitored location
- Extract core fields from clean invoices
- Detect low-quality or incomplete invoices and send them to review
- Detect duplicates using rule-based logic: **same invoice ID**, and/or **same vendor + invoice date + total amount** within tolerance against previously processed items in the batch *(reference implementation in `process_invoice.py`)*
- Log decisions consistently in a structured format
- Generate a daily summary of processing outcomes
- Demonstrate clear business value in an interview setting

---

## 6. Scope

### In Scope
- Synthetic invoice dataset generation
- Different invoice types and layouts
- Clean, noisy, duplicate and suspicious invoice scenarios
- **Delivered:** Python batch pipeline over invoice files + evaluation vs. ground truth
- **Original platform target (not delivered as live flows):** Power Automate ingestion from SharePoint/OneDrive
- AI-based invoice field extraction **(OpenAI in this repo)**
- Business rule validation and duplicate detection **(implemented in Python)**
- **Delivered:** structured logging as **CSV** (`predictions.csv`, `comparison_results.csv`)
- **Original target:** logging to SharePoint list or Excel table
- Human review **as a design outcome** (`Needs review` + reasons); **no separate queue app** in repo
- **Original target:** daily summary flow in Power Automate *(not in Python MVP)*
- Architecture documentation
- Test matrix and test execution
- Interview-ready narrative that distinguishes **intent (Power Platform)** from **reference build (Python)**

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
The solution shall detect likely duplicates using rules consistent with the reference implementation:
- **Primary:** same **Invoice ID** (invoice number) as a previously processed invoice in the batch
- **Fallback:** same **vendor** + same **invoice date** + same **total amount** (within a small tolerance)

*(A simpler “vendor + invoice ID + amount” check remains a valid interview variant for a datastore-backed system; the batch Python code uses the rules above.)*

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
Python scripts that generate invoice documents and expected-output metadata *(delivered / supported in repo)*.

### Originally targeted platform (Power Automate + M365 + Azure)

These components reflect the **first integration plan**. They are **not implemented as working flows** in this repository because of environment constraints (see **Document status**).

#### Component B — Storage Layer (target)
OneDrive or SharePoint folder for incoming invoice files.

#### Component C — Extraction Layer (target)
Power Automate flow with AI Builder and/or **Azure AI Document Intelligence** action.

#### Component D — Rule Engine (target)
Conditions in Power Automate for missing fields, low confidence, duplicates, suspicious dates, vendor whitelist, high amount.

#### Component E — Logging Layer (target)
SharePoint list or Excel table with structured processing results.

#### Component F — Review Layer (target)
Simple queue/list where uncertain invoices can be reviewed.

#### Component G — Reporting Layer (target)
Daily summary flow via email or Teams.

### As implemented in this repository (Python reference)

| Concern | Implementation |
|--------|------------------|
| Intake | Batch read from `data/generated_invoices/` |
| Text from PDF | `pdfplumber` in `process_invoice.py` |
| Structured extraction | OpenAI Responses API (`gpt-4.1-mini` in code) |
| Rules / duplicates | Functions `validate`, `detect_duplicate`, `classify` |
| Logging | `predictions.csv`, `comparison_results.csv`, console output |
| Evaluation | `batch_eval.py` vs. ground truth CSV |
| Daily summary | Out of scope for current code *(PRD placeholder for PA)* |

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
If **same invoice ID** as a prior item already exists, **or** (fallback) **same vendor + same invoice date + same total amount** within tolerance:
- Status = Suspected duplicate / routed to review *(reference Python: `Needs review` with duplicate metadata)*

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
- AI extraction may require credits or limited access *(OpenAI API in delivered path)*
- Invoice formats may vary too much
- Time is limited
- **Realized:** Power Platform **tenant/licensing/provisioning** blocked end-to-end Power Automate + SharePoint + AI Builder + Azure Document Intelligence *(see Document status)*
- Local tooling (e.g. Poppler / `pdf2image`) can complicate noisy-PDF workflows on some machines

### Assumptions
- **For the Python reference:** `OPENAI_API_KEY` and Python dependencies are available
- **Original plan assumed:** Power Automate, SharePoint or Excel logging, and AI Builder or Azure Document Intelligence—**these were not all available** in the developer tenant used for the case
- Synthetic data is sufficient for demo purposes

---

## 17. Fallback Strategy
**Primary fallback taken:** Implement the **Python pipeline** with **OpenAI** for extraction, **rule-based** validation and duplicates, and **CSV + ground truth** evaluation so the case remains **end-to-end and measurable** without Power Platform backend.

If AI extraction is not available at all:
- Simulate extraction via pre-generated metadata
- Continue with routing, validation, logging and review logic
- Be transparent in interview about what was simulated

**Always** be transparent that **Power Automate integration was intended** but **not shipped** in this repo; the Python code is the **delivered reference**.

---

## 18. Deliverables
1. Synthetic invoice dataset *(delivered under `data/`)*  
2. Ground truth CSV *(delivered)*  
3. **Original target:** Power Automate Flow 1: Intake + Extraction + Logging *(not completed as PA—substituted by Python batch + extraction + CSV logging)*  
4. **Original target:** Power Automate Flow 2: Validation + Routing *(logic in `process_invoice.py`)*  
5. **Original target:** Power Automate Flow 3: Daily Summary *(not in Python MVP)*  
6. Optional human review flow *(conceptual via `Needs review`; no separate PA flow in repo)*  
7. Architecture document *(PRD + `docs/` + `README.md`)*  
8. Test matrix  
9. Test results  
10. Interview pitch *(clarify intent vs. Python delivery)*  

---

## 19. Definition of Done
**For the Python reference (this repo), “done” means:**
- A **folder of invoice files** can be batch-processed reproducibly
- A representative **synthetic dataset** and **ground truth** exist *(current set may be smaller than 30; PRD volume remains a stretch goal)*
- **Extraction** works via OpenAI *(or documented simulation if keys unavailable)*
- **Business rules** route invoices into the intended status categories for the implemented scope
- Results are **logged** to CSV (and traceable reasons exist)
- **Test cases** are executed and documented
- Documentation **explicitly states** Power Platform intent vs. Python delivery
- A concise **interview story** is ready

**Full PRD “done” including Power Automate** would additionally require a provisioned tenant, flows, and daily summary—**out of scope for the delivered repository**.

---

## 20. Interview Positioning
This project should be presented not as “a cool demo,” but as:
- A business automation use case
- A realistic AP/finance workflow
- An example of combining AI + automation + governance + human review
- A case designed with scalability and operational reasoning in mind

**Credibility line:** *“I targeted Power Automate and the Microsoft stack for the full integration, but the tenant didn’t have SharePoint/OneDrive/AI Builder/Azure set up correctly—so I shipped a Python reference pipeline that proves the same ingest → extract → validate → route → measure story and ground-truth evaluation.”*

---

# PRD — AI-driven fakturaintag, validering och granskningspipeline (svensk version)

## Dokumentstatus (läs först)

**Ursprunglig avsikt:** Caset var först scope:at mot **Microsoft Power Platform** — **Power Automate** för orkestrering, **SharePoint eller OneDrive** för intag/lagring, **AI Builder** och/eller **Azure AI Document Intelligence** (Form Recognizer) för extraktion, samt strukturerad loggning i SharePoint eller Excel (och valfri daglig sammanfattning via e-post/Teams).

**Varför den integrationen inte slutfördes:** Miljön saknade en fullt provisionerad Microsoft 365 / Azure-backend: begränsade rättigheter i tenanten, **ingen aktiv SharePoint-webbplats** för standardkopplingar, **OneDrive** gick inte att lita på som trigger, **ingen AI Builder-premiumlicens** och **ingen Azure-prenumeration** (därmed inga nycklar eller endpoint för Document Intelligence). **Spärren var licensiering, provisioning och behörigheter — inte affärsdesignen.**

**Vad detta repo faktiskt levererar:** En **Python-referensimplementation** (`docs/src/process_invoice.py`, `docs/src/batch_eval.py`, `README.md`) som implementerar **samma logiska pipeline**: läsa faktura-PDF:er från mapp (batch), extrahera text (`pdfplumber`), strukturerad fältextraktion via **OpenAI**, normalisering och validering, **regelbaserad dubblettdetektering** (samma faktura-ID, eller samma leverantör + fakturadatum + totalbelopp inom tolerans mot tidigare poster i batchen), dirigering till `Approved` eller `Needs review`, samt **mätbar utvärdering** mot ground truth-CSV. **Detta är inte en driftsatt Power Automate-lösning**, utan ett end-to-end, testbart substitut för demo och intervju.

**Intervjuformulering:** Börja med **affärsproblem och system** (intag → extraktion → validering → dirigering → mätning). Var tydlig med att **Power Automate var det planerade integrationslagret** men att E2E inte kunde färdigställas i den tillgängliga tenanten; Python-pipelinen **bevisar reglerna, AI-stödd extraktion och kvalitetsmått** som i produktion skulle kunna ligga bakom motsvarande kopplingar i Power Platform/Azure.

---

## 1. Projekttitel
AI-driven fakturaintag, validering och granskningspipeline *(PRD:s produktintention; **referensimplementation = Python i detta repo**, inte en färdig Power Automate-integration)*

---

## 2. Bakgrund
Många organisationer tar emot fakturor via e-post eller dokumentmappar i flera format och med olika kvalitet. Manuell fakturahantering är långsam, felbenägen och svår att skala. Projektet ska simulera ett realistiskt konsultcase där inkommande fakturor tas emot, analyseras med AI, valideras med affärsregler och dirigeras antingen till automatisk hantering eller manuell granskning.

Projektet är utformat som ett portfolio-case för intervjuer inom AI, automation, processförbättring och affärsnytta.

**Implementationsnotering:** Första designmålet var **Power Automate** med **SharePoint/OneDrive**, **AI Builder** och/eller **Azure AI Document Intelligence**. Leverans end-to-end på Power Platform **var inte möjlig** i den tenant som användes i caset — se **Dokumentstatus** ovan. **Den levererade mjukvaran** är Python-pipelinen i detta repo, i linje med samma teman (spårbarhet, regler, manuell granskning vid osäkerhet, testbarhet).

---

## 3. Problembeskrivning
Ekonomi- och operationsteam lägger ofta för mycket tid på repetitiv fakturahantering:
- Öppna bilagor manuellt
- Läsa fakturametadata manuellt
- Registrera leverantör, belopp, datum och fakturanummer manuellt
- Upptäcka dubbletter eller misstänkta fakturor för sent
- Eskalera ofullständiga eller lågkvalitativa fakturor manuellt

Verksamheten behöver en lösning som:
- Minskar repetitivt manuellt arbete
- Ökar hastigheten i intaget
- Förbättrar datakvaliteten
- Identifierar misstänkta eller ofullständiga fakturor
- Bevarar manuell granskning i osäkra fall

---

## 4. Mål
Leverera en realistisk pipeline för fakturaautomation som kan:
1. Ta emot fakturor från en mapp *(batch-katalog i Python-bygget; övervakad mapp var målet i Power Automate)*
2. Extrahera strukturerad fakturadata *(OpenAI i repot; AI Builder / Document Intelligence i den ursprungliga plattformsplanen)*
3. Tillämpa validering och affärsregler
4. Dirigera fakturor till:
   - Godkänd (Approved)
   - Behöver granskning (Needs review)
   - *(PRD beskriver även misstänkt dubblett/bedrägeri; referenskoden fokuserar på `Approved` / `Needs review` med dubblett som metadata — kan utökas)*
5. Logga alla utfall *(CSV + terminal i Python; SharePoint/Excel i originalplanen)*
6. Ta fram en daglig sammanfattning *(ej i Python-MVP — tänkt som separat Power Automate-flöde)*
7. Stödja en enkel manuell granskningsprocess *(via `Needs review` och orsakssträngar; ingen separat kö-UI i repot)*

---

## 5. Framgångskriterier
Lösningen anses lyckad om den kan:
- Bearbeta minst 30 syntetiska fakturor
- Korrekt ta emot filer från en övervakad plats
- Extrahera kärnfält från rena fakturor
- Upptäcka lågkvalitativa eller ofullständiga fakturor och skicka dem till granskning
- Upptäcka dubbletter med regler: **samma faktura-ID**, och/eller **samma leverantör + fakturadatum + totalbelopp** inom tolerans mot tidigare bearbetade poster i batchen *(referensimplementation i `process_invoice.py`)*
- Logga beslut konsekvent i ett strukturerat format
- Generera en daglig sammanfattning av bearbetningsutfall
- Visa tydlig affärsnytta i en intervjusituation

---

## 6. Omfattning

### Inom omfattning
- Generering av syntetiskt fakturadataset
- Olika fakturatyper och layouter
- Scenarier med rena, stökiga, duplicerade och misstänkta fakturor
- **Levererat:** Python-batchpipeline över fakturafiler + utvärdering mot ground truth
- **Ursprunglig plattformsmålbild (ej levererat som live-flöden):** inflöde i Power Automate från SharePoint/OneDrive
- AI-baserad extraktion av fakturafält **(OpenAI i detta repo)**
- Affärsregelvalidering och dubblettdetektering **(implementerat i Python)**
- **Levererat:** strukturerad loggning som **CSV** (`predictions.csv`, `comparison_results.csv`)
- **Målbild:** loggning till SharePoint-lista eller Excel-tabell
- Manuell granskning **som designutfall** (`Needs review` + orsaker); **ingen separat kö-app** i repot
- **Målbild:** flöde för daglig sammanfattning i Power Automate *(saknas i Python-MVP)*
- Arkitekturdokumentation
- Testmatris och testkörning
- Berättelse redo för intervju som skiljer **avsikt (Power Platform)** från **referensbygge (Python)**

### Utanför omfattning
- Verklig ERP-integration
- Verklig bokföring
- Verklig leverantörsbetalning
- Säkerhetsmodell i produktionsklass
- Bedrägeridetektering i produktionsklass
- Avancerad front-end-UX
- Komplex Power Apps-lösning om tid inte räcker

---

## 7. Primära användarpersonas

### Persona 1 — Ekonomi/AP-medarbetare
Behöver att inkommande fakturor hanteras snabbare med färre manuella steg.

### Persona 2 — Granskare/revisor
Behöver att misstänkta eller ofullständiga fakturor flaggas med tydliga orsaker.

### Persona 3 — Automationskonsult
Behöver en lösning som är förklarlig, testbar och tydligt kopplad till affärsnytta.

---

## 8. Användarberättelser

### Intag
Som ekonomimedarbetare vill jag att fakturor som läggs i en mapp bearbetas automatiskt så att jag inte behöver granska varje fil manuellt.

### Extraktion
Som ekonomimedarbetare vill jag att fakturanummer, leverantörsnamn, datum och totalbelopp extraheras automatiskt så att manuell registrering minskar.

### Validering
Som granskare vill jag att fakturor med saknade fält, låg confidence, dubbletter eller misstänkta värden dirigeras till granskning så att riskfylld data inte auto-godkänns.

### Loggning
Som konsult vill jag att varje bearbetad faktura loggas med status och orsak så att jag kan visa spårbarhet och styrning (governance).

### Granskning
Som granskare vill jag en enkel granskningskö så att jag kan godkänna eller avvisa osäkra fakturor.

### Rapportering
Som chef vill jag en daglig sammanfattning av bearbetade fakturor så att jag kan förstå automationens prestanda.

---

## 9. Funktionella krav

### FR1 — Filintag
Lösningen ska övervaka en angiven mapp för nya fakturafiler.

### FR2 — Stödda filtyper
Lösningen bör stödja PDF och bildbaserade fakturor för test.

### FR3 — AI-extraktion
Lösningen ska försöka extrahera:
- Leverantörsnamn
- Faktura-ID
- Fakturadatum
- Förfallodatum
- Valuta
- Momsbelopp
- Totalbelopp

### FR4 — Validering av obligatoriska fält
Lösningen ska skicka fakturor till granskning om kritiska fält saknas.

### FR5 — Confidence-validering
Lösningen ska skicka fakturor till granskning när extraktionens confidence understiger en vald tröskel.

### FR6 — Dubblettdetektering
Lösningen ska upptäcka sannolika dubbletter med regler i linje med referensimplementationen:
- **Primär:** samma **faktura-ID** (fakturanummer) som en tidigare bearbetad faktura i batchen
- **Reserv:** samma **leverantör** + samma **fakturadatum** + samma **totalbelopp** (inom liten tolerans)

*(En enklare kontroll ”leverantör + faktura-ID + belopp” mot en datalagerbakgrund är fortfarande en giltig intervjvariant; batch-Python-koden använder reglerna ovan.)*

### FR7 — Detektering av misstänkta mönster
Lösningen ska flagga misstänkta fakturor när:
- Förfallodatum är tidigare än fakturadatum
- Beloppet är ovanligt högt
- Leverantören inte finns på vitlista
- Fält verkar inkonsekventa

### FR8 — Loggning
Lösningen ska lagra bearbetad fakturadata och status i en strukturerad logg.

### FR9 — Granskningskö
Lösningen ska skriva fakturor som kräver granskning till en separat granskningskö eller tydligt markera dem i loggen.

### FR10 — Daglig sammanfattning
Lösningen ska producera en daglig sammanfattning med antal per utfallskategori.

---

## 10. Icke-funktionella krav

### NFR1 — Förklarbarhet
Flödet måste vara lätt att förklara i en intervju.

### NFR2 — Spårbarhet
Varje beslut ska ha en kopplad orsak.

### NFR3 — Testbarhet
Projektet ska innehålla testdata, förväntade utfall och en testmatris.

### NFR4 — Modularitet
Lösningen ska vara uppdelad i tydliga flöden och återanvändbara dataassets.

### NFR5 — Realism
Användningsfallet ska kännas tillräckligt realistiskt för en diskussion om konsulting/automation.

---

## 11. Design av indataset

### Kategorier
1. Rena fakturor
2. Stökiga men legitima fakturor
3. Fakturor med saknade fält
4. Duplicerade fakturor
5. Misstänkta/falska fakturor

### Målvolym
Minst 30 fakturor totalt.

### Exempelfördelning
- 10 rena
- 8 stökiga
- 6 med saknade fält
- 3 dubbletter
- 5 misstänkta/falska

---

## 12. Ground truth / förväntat utfall
Varje faktura ska ha en motsvarande förväntad utdatarad som inkluderar:
- Filnamn
- Förväntad leverantör
- Förväntat faktura-ID
- Förväntat fakturadatum
- Förväntat förfallodatum
- Förväntad valuta
- Förväntat totalbelopp
- Kategori
- Förväntat utfall
- Anteckningar

Förväntade utfall:
- Godkänd (Approved)
- Behöver granskning (Needs review)
- Misstänkt dubblett (Suspected duplicate)
- Misstänkt bedrägeri (Suspected fraud)

---

## 13. Föreslagna systemkomponenter

### Komponent A — Generator av syntetisk data
Python-skript som genererar fakturadokument och metadata för förväntade utfall *(stöds/levereras i repot)*.

### Ursprungligen målad plattform (Power Automate + M365 + Azure)

Dessa komponenter beskriver **första integrationsplanen**. De är **inte implementerade som fungerande flöden** i detta repo på grund av miljöbegränsningar (se **Dokumentstatus**).

#### Komponent B — Lagringslager (målbild)
OneDrive- eller SharePoint-mapp för inkommande fakturafiler.

#### Komponent C — Extraktionslager (målbild)
Power Automate-flöde med AI Builder och/eller **Azure AI Document Intelligence**.

#### Komponent D — Regelmotor (målbild)
Villkor i Power Automate för saknade fält, låg confidence, dubbletter, misstänkta datum, leverantörsvitlista, höga belopp.

#### Komponent E — Loggningslager (målbild)
SharePoint-lista eller Excel-tabell med strukturerade bearbetningsresultat.

#### Komponent F — Granskningslager (målbild)
Enkel kö/lista där osäkra fakturor kan granskas.

#### Komponent G — Rapporteringslager (målbild)
Dagligt sammanfattningsflöde via e-post eller Teams.

### Som implementerat i detta repo (Python-referens)

| Område | Implementation |
|--------|----------------|
| Intag | Batchläsning från `data/generated_invoices/` |
| Text från PDF | `pdfplumber` i `process_invoice.py` |
| Strukturerad extraktion | OpenAI Responses API (`gpt-4.1-mini` i koden) |
| Regler / dubbletter | Funktionerna `validate`, `detect_duplicate`, `classify` |
| Loggning | `predictions.csv`, `comparison_results.csv`, konsolutskrift |
| Utvärdering | `batch_eval.py` mot ground truth-CSV |
| Daglig sammanfattning | Utanför nuvarande kod *(platshållare för PA)* |

---

## 14. Definitioner av status

### Godkänd (Approved)
Fakturan passerade extraktions- och valideringskontroller.

### Behöver granskning (Needs review)
Fakturan kunde inte lita på automatiskt och kräver manuell granskning.

### Misstänkt dubblett (Suspected duplicate)
Fakturan verkar matcha en tidigare faktura enligt dubblettlogik.

### Misstänkt bedrägeri (Suspected fraud)
Fakturan har misstänkta mönster och bör granskas med hög prioritet.

---

## 15. Affärsregler

### Regelgrupp A — Saknade fält
Om leverantörsnamn, faktura-ID, fakturadatum eller totalbelopp saknas:
- Status = Behöver granskning (Needs review)

### Regelgrupp B — Låg confidence
Om confidence understiger tröskel:
- Status = Behöver granskning (Needs review)

### Regelgrupp C — Dubblettdetektering
Om **samma faktura-ID** som en tidigare post finns, **eller** (reserv) **samma leverantör + samma fakturadatum + samma totalbelopp** inom tolerans:
- Status = Misstänkt dubblett / dirigerad till granskning *(Python-referens: `Needs review` med dubblettmetadata)*

### Regelgrupp D — Leverantörsvitlista
Om leverantören inte finns i godkänd leverantörslista:
- Status = Behöver granskning eller Misstänkt bedrägeri beroende på kontext

### Regelgrupp E — Datumlogik
Om förfallodatum är tidigare än fakturadatum:
- Status = Misstänkt bedrägeri (Suspected fraud)

### Regelgrupp F — Beloppslogik
Om belopp överstiger avvikelsetröskel:
- Status = Behöver granskning (Needs review)

---

## 16. Risker och antaganden

### Risker
- AI-extraktion kan kräva credits eller begränsad åtkomst *(OpenAI API i levererad väg)*
- Fakturaformat kan variera för mycket
- Tiden är begränsad
- **Uppfyllt i caset:** Power Platform-**tenant/licens/provisioning** spärrade E2E med Power Automate + SharePoint + AI Builder + Azure Document Intelligence *(se Dokumentstatus)*
- Lokala verktyg (t.ex. Poppler / `pdf2image`) kan krångla vid brusiga PDF:er på vissa maskiner

### Antaganden
- **För Python-referensen:** `OPENAI_API_KEY` och Python-beroenden finns
- **Ursprungsplanen förutsatte:** Power Automate, SharePoint- eller Excel-loggning samt AI Builder eller Document Intelligence — **detta var inte fullt tillgängligt** i den utvecklartenant som användes
- Syntetisk data räcker för demonstrationsändamål

---

## 17. Fallback-strategi
**Primär fallback som använts:** Implementera **Python-pipelinen** med **OpenAI** för extraktion, **regelbaserad** validering och dubbletter samt **CSV + ground truth**-utvärdering så att caset förblir **end-to-end och mätbart** utan Power Platform-backend.

Om AI-extraktion inte alls är tillgänglig:
- Simulera extraktion via förgenererad metadata
- Fortsätt med dirigering, validering, loggning och granskningslogik
- Var transparent i intervjun om vad som simulerats

**Var alltid tydlig** med att **Power Automate-integration var avsikten** men **inte levererad** i detta repo; Python-koden är **referensimplementationen**.

---

## 18. Leverabler
1. Syntetiskt fakturadataset *(under `data/`)*  
2. Ground truth CSV *(levererad)*  
3. **Målbild:** Power Automate-flöde 1: Intag + extraktion + loggning *(ej klart som PA — ersatt av Python-batch + extraktion + CSV-loggning)*  
4. **Målbild:** Power Automate-flöde 2: Validering + dirigering *(logik i `process_invoice.py`)*  
5. **Målbild:** Power Automate-flöde 3: Daglig sammanfattning *(saknas i Python-MVP)*  
6. Valfritt flöde för manuell granskning *(koncept via `Needs review`; inget separat PA-flöde i repot)*  
7. Arkitekturdokument *(PRD + `docs/` + `README.md`)*  
8. Testmatris  
9. Testresultat  
10. Intervjupitch *(tydliggör avsikt vs. Python-leverans)*  

---

## 19. Definition av klart
**För Python-referensen (detta repo) innebär ”klart”:**
- En **mapp med fakturafiler** kan batch-bearbetas reproducerbart
- Ett representativt **syntetiskt dataset** och **ground truth** finns *(nuvarande uppsättning kan vara färre än 30; PRD-volym kvarstår som stretchmål)*
- **Extraktion** fungerar via OpenAI *(eller dokumenterad simulering om nycklar saknas)*
- **Affärsregler** dirigerar till avsedda statuskategorier inom implementerat omfång
- Resultat **loggas** till CSV (med spårbara orsaker)
- **Testfall** har körts och dokumenterats
- Dokumentation **säger uttryckligen** Power Platform-avsikt vs. Python-leverans
- En koncis **intervjuberättelse** är färdig

**Full PRD ”klart” inklusive Power Automate** skulle dessutom kräva provisionerad tenant, flöden och daglig sammanfattning — **det ligger utanför det levererade repot**.

---

## 20. Positionering i intervjun
Projektet ska presenteras inte som ”en cool demo”, utan som:
- Ett affärsautomation-use-case
- Ett realistiskt AP/ekonomiflöde
- Ett exempel på kombinationen AI + automation + styrning (governance) + manuell granskning
- Ett case utformat med skalbarhet och operativt resonemang i åtanke

**Trovärdighetsrad:** *”Jag siktade på Power Automate och Microsoft-stacken för full integration, men tenanten hade inte SharePoint/OneDrive/AI Builder/Azure uppsatt som krävs — då levererade jag en Python-referenspipeline som visar samma historia intag → extraktion → validering → dirigering → mätning med ground truth.”*
