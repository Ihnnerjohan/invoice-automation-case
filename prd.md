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

---

# PRD — AI-driven fakturaintag, validering och granskningspipeline (svensk version)

## 1. Projekttitel
AI-driven fakturaintag, validering och granskningspipeline i Power Automate

---

## 2. Bakgrund
Många organisationer tar emot fakturor via e-post eller dokumentmappar i flera format och med olika kvalitet. Manuell fakturahantering är långsam, felbenägen och svår att skala. Projektet ska simulera ett realistiskt konsultcase där inkommande fakturor tas emot, analyseras med AI, valideras med affärsregler och dirigeras antingen till automatisk hantering eller manuell granskning.

Projektet är utformat som ett portfolio-case för intervjuer inom AI, automation, processförbättring och affärsnytta.

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
Bygga en realistisk pipeline för fakturaautomation med Power Automate och AI-tjänster som kan:
1. Ta emot fakturor från en mapp
2. Extrahera strukturerad fakturadata
3. Tillämpa validering och affärsregler
4. Dirigera fakturor till:
   - Godkänd (Approved)
   - Behöver granskning (Needs review)
   - Misstänkt dubblett/bedrägeri
5. Logga alla utfall
6. Ta fram en daglig sammanfattning
7. Stödja en enkel manuell granskningsprocess

---

## 5. Framgångskriterier
Lösningen anses lyckad om den kan:
- Bearbeta minst 30 syntetiska fakturor
- Korrekt ta emot filer från en övervakad plats
- Extrahera kärnfält från rena fakturor
- Upptäcka lågkvalitativa eller ofullständiga fakturor och skicka dem till granskning
- Upptäcka dubbletter med logik baserad på faktura-ID, leverantör och belopp
- Logga beslut konsekvent i ett strukturerat format
- Generera en daglig sammanfattning av bearbetningsutfall
- Visa tydlig affärsnytta i en intervjusituation

---

## 6. Omfattning

### Inom omfattning
- Generering av syntetiskt fakturadataset
- Olika fakturatyper och layouter
- Scenarier med rena, stökiga, duplicerade och misstänkta fakturor
- Inflöde (ingestion) i Power Automate
- AI-baserad extraktion av fakturafält
- Affärsregelvalidering
- Loggning till SharePoint-lista eller Excel-tabell
- Kö för manuell granskning
- Flöde för daglig sammanfattning
- Arkitekturdokumentation
- Testmatris och testkörning
- Berättelse redo för intervju

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
Lösningen ska upptäcka sannolika dubbletter baserat på:
- Leverantörsnamn
- Faktura-ID
- Totalbelopp

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
Python-skript i Cursor som genererar fakturadokument och metadata för förväntade utfall.

### Komponent B — Lagringslager
OneDrive- eller SharePoint-mapp för inkommande fakturafiler.

### Komponent C — Extraktionslager
Power Automate-flöde med AI-åtgärd för extraktion.

### Komponent D — Regelmotor
Villkor i Power Automate för:
- Saknade fält
- Låg confidence
- Dubbletter
- Misstänkta datum
- Kontroll mot leverantörsvitlista
- Kontroll av höga belopp

### Komponent E — Loggningslager
SharePoint-lista eller Excel-tabell med strukturerade bearbetningsresultat.

### Komponent F — Granskningslager
Enkel kö/lista där osäkra fakturor kan granskas.

### Komponent G — Rapporteringslager
Dagligt sammanfattningsflöde via e-post eller Teams.

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
Om samma leverantör + samma faktura-ID + samma belopp redan finns:
- Status = Misstänkt dubblett (Suspected duplicate)

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
- AI-extraktion kan kräva credits eller begränsad åtkomst
- Fakturaformat kan variera för mycket
- Tiden är begränsad
- Inloggnings-/miljöproblem i Power Platform

### Antaganden
- En Power Automate-miljö finns tillgänglig
- AI-extraktion är tillgänglig eller kan simuleras
- Syntetisk data räcker för demonstrationsändamål
- SharePoint- eller Excel-loggning finns tillgänglig

---

## 17. Fallback-strategi
Om AI-extraktion inte är tillgänglig:
- Simulera extraktion via förgenererad metadata
- Fortsätt med dirigering, validering, loggning och granskningslogik
- Var transparent i intervjun om vad som simulerats

---

## 18. Leverabler
1. Syntetiskt fakturadataset
2. Ground truth CSV
3. Power Automate-flöde 1: Intag + extraktion + loggning
4. Power Automate-flöde 2: Validering + dirigering
5. Power Automate-flöde 3: Daglig sammanfattning
6. Valfritt flöde för manuell granskning
7. Arkitekturdokument
8. Testmatris
9. Testresultat
10. Intervjupitch

---

## 19. Definition av klart
Projektet är klart när:
- En övervakad mapp tar emot fakturor
- Minst 30 fakturor finns tillgängliga
- Extraktion fungerar eller är trovärdigt simulerad
- Affärsregler dirigerar fakturor till rätt kategorier
- Resultat loggas
- Daglig sammanfattning fungerar
- Testfall har körts
- Dokumentationen är komplett
- En koncis intervjuberättelse är färdig

---

## 20. Positionering i intervjun
Projektet ska presenteras inte som ”en cool demo”, utan som:
- Ett affärsautomation-use-case
- Ett realistiskt AP/ekonomiflöde
- Ett exempel på kombinationen AI + automation + styrning (governance) + manuell granskning
- Ett case utformat med skalbarhet och operativt resonemang i åtanke
